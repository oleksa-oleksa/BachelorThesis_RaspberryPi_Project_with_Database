from django.db import models
from django.forms import ModelForm
from django_enumfield import enum
from django.core.exceptions import ValidationError
import datetime
from django_fsm import FSMField, transition, RETURN_VALUE, GET_STATE
from django.core.exceptions import ValidationError


class ATRCardType(enum.Enum):
	"""Constant values for ATR ot student card and RFID tags on the Raspberry Pi"""
	STUDENT_CARD_ATR = 1
	RASPI_TAG_ATR = 2


class StudentCard(models.Model):
	"""
	Student card class
	Primary key = default django primary key
	Each card contains an integrated chip with a permanent identification number, or UID. 
	This number is created during the manufacturing process, it is sometimes referred to as the card serial number.
	
	One unique student card belongs to only one student
	"""
	atr_hex = enum.EnumField(ATRCardType, default=ATRCardType.STUDENT_CARD_ATR)
	uid = models.CharField('Card UID', max_length=66, unique=True)

	def __str__(self):
		return self.uid


class RaspiTag(models.Model):
	"""
	Raspberry board RFID
	Primary key = default django primary key
	One unique rfig tag belongs to one physical Raspberry Board
	"""
	atr_hex = enum.EnumField(ATRCardType, default=ATRCardType.RASPI_TAG_ATR)
	uid = models.CharField('Card UID', max_length=66, unique=True)

	def __str__(self):
		return self.uid


class StudentGroup(enum.Enum):
	A_GROUP = 1
	B_GROUP = 2
	

class Operation(enum.Enum):
	"""Represents different operations that could be done by student or admin on loan system"""
	LAB_LOAN = 1
	HOME_LOAN = 2
	RETURN_BOARD = 3
	ENABLE_HOME_LOAN = 4
	DISABLE_HOME_LOAN = 5
	START_SESSION = 6
	UNKNOWN_OPERATION = 7


class BoardType(enum.Enum):
	"""Represents two types of boards: for laboratory usage only and for home loan only"""
	LAB_LOAN = 1
	HOME_LOAN = 2


class BoardStatus(enum.Enum):
	ACTIVE = 1
	LOANED = 2
	OUT_OF_ORDER = 3
	LOST = 4
	UNDEFINED = 5


class Semester(models.Model):
	semester = models.CharField(max_length=20, unique=True)

	def __str__(self):
		return self.semester


class Student(models.Model):
	"""
	Represents a student in database. The personal date will be specified
	by the admin after student has made enrollment to the course.
	The group will be specified on the first lecture by the students/teaching assistance
	home_loan_enabled flag is to set by the admin in case the board was returned damaged
	and a student has not notified the teaching assistance about what happened

	Primary key = default django primary key
	Each student has only one unuqie student card
	"""
	student_card = models.OneToOneField(StudentCard, on_delete=models.SET_NULL, blank=True, null=True)
	semester = models.ForeignKey(Semester, on_delete=models.CASCADE, blank=True, null=True)
	first_name = models.CharField('first name', max_length=50)
	second_name = models.CharField('second name', max_length=50)
	matricul_no = models.CharField('matriculation', max_length=10, unique=True)
	hrz_no = models.CharField('hrz', max_length=10, unique=True)
	group = enum.EnumField(StudentGroup)
	is_home_loan_enabled = models.BooleanField(default=True)
	
	class Meta:
		ordering = ['second_name']

	def __str__(self):
		return self.first_name + ' ' + self.second_name

	def get_student_boards(self):
		# boards = {"lab": "", "home": ""}
		boards = {}
		lab_board_action = self.action_set.filter(operation=Operation.LAB_LOAN).last()
		home_board_action = self.action_set.filter(operation=Operation.HOME_LOAN).last()

		if lab_board_action is not None:
			if lab_board_action.board.board_status == BoardStatus.LOANED:
				boards["lab"] = lab_board_action.board

		if home_board_action is not None:
			if home_board_action.board.board_status == BoardStatus.LOANED:
				boards["home"] = home_board_action.board

		return boards


class Board(models.Model):
	"""
	Class for representation of the Raspberry Pi board at university laboratory
	There are 15 boards and every board has a number and a RFID Tag on it.
	The boards numbered 0-10 should be used in the laboratory during the exercise lesson (BoardLabLoan class)
	The boards numbered 11-15 could be loaned by authorised student for home usage (BoardHomeLoan class)
	Primary key = default django primary key
	Each board has only one unuqie rfid tag
	"""
	raspi_tag = models.OneToOneField(RaspiTag, on_delete=models.SET_NULL, blank=True, null=True)
	board_no = models.IntegerField('board number', unique=True)
	board_type = enum.EnumField(BoardType, default=BoardType.LAB_LOAN)
	board_status = enum.EnumField(BoardStatus, default=BoardStatus.ACTIVE)
	
	class Meta:
		ordering = ['board_no']
		
	def __str__(self):
		if self.raspi_tag is not None:
			return 'Board ' + str(self.board_no)
		else:
			return 'Board ' + str(self.board_no)


class Action(models.Model):
	"""
	Holds the record about the loan operation, student, board and time
	Primary key = default django primary key
	"""
	student = models.ForeignKey(Student, on_delete=models.SET_NULL, blank=True, null=True)
	board = models.ForeignKey(Board, on_delete=models.SET_NULL, blank=True, null=True)
	timestamp = models.DateTimeField(default=datetime.datetime.now)
	operation = enum.EnumField(Operation, default=Operation.UNKNOWN_OPERATION)

	class Meta:
		ordering = ['timestamp']

	@staticmethod
	def return_lab_board(student, board, timestamp=datetime.datetime.now, operation=Operation.RETURN_BOARD):
		returned_board = Action(student, board, timestamp, operation)
		returned_board.save()


class Session(models.Model):
	"""
	Holds the information about the interaction between user (student) and system
	Primary key = default django primary key
	"""

	TERMINAL_STATES = ['timeout', 'finished']

	start_time = models.DateTimeField(default=datetime.datetime.now)
	state = FSMField(default='session_started')
	last_action_time = models.DateTimeField(auto_now=True)
	student_card = models.ForeignKey(StudentCard, on_delete=models.SET_NULL, blank=True, null=True, related_name='+')
	raspi_tag = models.ForeignKey(RaspiTag, on_delete=models.SET_NULL, blank=True, null=True, related_name='+')

	class Meta:
		ordering = ['id']

	@staticmethod
	def get_active_session():
		return Session.objects.exclude(state__in=Session.TERMINAL_STATES).last()

	def get_active_board(self):
		if self.raspi_tag is None:
			return None
		return self.raspi_tag.board

	def get_active_student(self):
		if self.student_card is None:
			return None
		return self.student_card.student

	def is_board_returned(self):
		student = self.get_active_student()
		boards = self.student_card.student.get_student_boards()
		scanned_board = self.get_active_board()

		# return loaned board that is assigned on student- OK
		if scanned_board in boards.values():
			# create action in Action model with returning operation and timestamp
			Action.return_lab_board(student, scanned_board)
			# returning by setting the status of the board to be "active"
			scanned_board.board_status = BoardStatus.ACTIVE
			return True
		else:
			return False

	def clean(self):
		open_session = Session.objects.exclude(state__in=Session.TERMINAL_STATES).count()
		if open_session != 0:
			raise ValidationError('Active session already exists!')
		super().clean()

	# =================== Django Final State Machine ===================================

	@transition(field=state, source='session_started', target='valid_student_card', on_error='unknown_student_card')
	def student_card_inserted(self, card_uid):
		card = StudentCard.objects.get(uid=card_uid)
		self.student_card = card

	@transition(field=state, source='valid_student_card', target='valid_rfid', on_error='unknown_rfid')
	def rfid_inserted(self, uid):
		tag = RaspiTag.objects.get(uid=uid)
		self.raspi_tag = tag

	@transition(field=state, source='valid_rfid', target=RETURN_VALUE('loaned', 'returned'))
	def action_created(self):
		if self.is_board_returned():
			return 'returned'
		else:
			return 'loaned'

	@transition(field=state, source='*', target='timeout')
	def timeout(self):
		pass

	@transition(field=state, source='*', target='canceled')
	def cancel(self):
		pass

	@transition(field=state, source=['unknown_student_card', 'banned_student',
									'returned', 'loaned', 'unknown_rfid'], target='finish')
	def finished(self):
		pass
