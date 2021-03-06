import datetime


def render_session(session):
    session_state = session.state

    student = session.get_active_student()
    if student is not None:
        student_first_name = student.first_name
        student_second_name = student.second_name
        session_student = student_first_name + " " + student_second_name

        boards = student.get_student_boards()

        if "lab" not in boards:
            loaned_lab_board = "No lab boards assigned."
            loaned_lab_board_operation = "You can take a board (1-11) to work during exercise time in lab."
        else:
            loaned_lab_board = "Lab board assigned to you: RaspiBoard " + str(boards["lab"].board_no)
            loaned_lab_board_operation = "You can return this board right now."

        if "home" not in boards:
            loaned_home_board = "No home loan board assigned."
            loaned_home_board_operation = "You can loan a board (12-16) to work at home."
        else:
            loaned_home_board = "Home board assigned to you: RaspiBoard " + str(boards["home"].board_no)
            loaned_home_board_operation = "You can return this board right now."

    else:
        session_student = ""
        loaned_lab_board = ""
        loaned_lab_board_operation = ""
        loaned_home_board = ""
        loaned_home_board_operation = ""

    scanned_board = session.get_active_board()
    if scanned_board is not None:
        session_board = "RaspiBoard " + str(scanned_board.board_no) + ' ' + str(scanned_board.board_type)
        operation = "Board ID is scanned."

        if session_state == "rfid_state_loaned":
            operation = "Scanned board has been loaned. It can be returned now."

        if session_state == "rfid_state_active":
            operation = "Scanned board is ready for loan!"

        if session_state == "return_error":
            operation = "Error during return process. Please contact administrator or teacher assistant."

        if session_state == "loaned":
            operation = "Scanned board is assigned on you now"
    else:
        session_board = ""
        operation = "Please scan board"

    if session_state == "status_error":
        session_board = "RaspiBoard " + str(scanned_board.board_no) + ' ' + str(scanned_board.board_type) \
                        + ' status is: ' + str(scanned_board.board_status)

    session_dict = {"state": session_state, "student": session_student, "scanned_board": session_board,
                    "loaned_lab_board": loaned_lab_board, "loaned_lab_board_operation": loaned_lab_board_operation,
                    "loaned_home_board": loaned_home_board, "loaned_home_board_operation": loaned_home_board_operation,
                    "operation": operation}
    return session_dict
