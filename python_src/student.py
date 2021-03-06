class Student:
    """
    Represents a student in database. The personal date will be specified
    by the admin after student has made enrollment to the course.
    The group will be specified on the first lecture by the students/teaching assistance
    home_loan_enabled flag is to set by the admin in case the board was returned damaged
    and a student has not notified the teaching assistance about what happened
    list_of_board can contain maximum two boards: one loaned to work in the laboratory during exercise lesson
    and one taken for home_loan.
    """
    def __init__(self, studentcard_uid=None, first_name='',
                 second_name='', matricul_no='', hrz_no='',
                 group=None, is_home_loan_enabled=True, list_of_boards=[]):
        """Initialises a new student with given parameters"""
        self.studentcard_uid = studentcard_uid
        self.first_name = first_name
        self.second_name = second_name
        self.matricul_no = matricul_no
        self.hrz_no = hrz_no
        self.group = group
        self.is_home_loan_enabled = is_home_loan_enabled
        self.list_of_board = list_of_boards


