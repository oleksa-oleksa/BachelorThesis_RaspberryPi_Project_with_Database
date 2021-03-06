var session_refresh_timer
var active_session_id

function decorate_terminate_state(body) {
            $("#cancel_button_div").hide()
            $("#terminate_error_button_div").show()
            $("#return_button_div").hide()
            $("#loan_button_div").hide()
            $("#welcome_student").hide()
            $("#place_board").hide()
            $("#scan_card").hide()
            $("#use_reader").hide()
            $("#ok_picture").hide()
}

function decorate_success_state(body) {
            $("#finish_button_div").show()
            $("#cancel_button_div").hide()
            $("#terminate_error_button_div").hide()
            $("#return_button_div").hide()
            $("#loan_button_div").hide()
            $("#welcome_student").hide()
            $("#place_board").hide()
            $("#scan_card").hide()
            $("#use_reader").hide()
            $("#warning_picture").hide()
}

function handle_session_event(body) {
    console.log(body);

    if (body.state == "unknown_student_card") {
           $("#student_name").text("Unknown student card. You are not registered on this course." +
            "Please contact teaching assistant or administrator! Session is terminated")
    }

    if (body.state == "status_error") {
            $("#student_name").text("This board can not be loaned or returned.")
            $("#operation_info").text("Board status error. Ask teaching assistant or administrator for a help")
            decorate_terminate_state(body)
    }

    if (body.state == "unknown_rfid") {
            $("#student_name").text("Board ID is not detected.")
            $("#operation_info").text("Board ID error. Ask teaching assistant or administrator for a help")
            decorate_terminate_state(body)

    }


    if (body.state == "home_loan_disabled") {
            $("#student_name").text("You can not loan board to work a home")
            $("#operation_info").text("Home loan is disabled. Ask teaching assistant or administrator for a help")
            $("#warning_picture").show()
            decorate_terminate_state(body)
    }

    if (body.state == "maximum_boards_reached") {
            $("#student_name").text("Maximum amount of board is reached. You have to return a board first!")
            $("#operation_info").text("Too much board loaned!")
            $("#warning_picture").show()
            decorate_terminate_state(body)
    }

    if (body.state == "same_board_type") {
            $("#student_name").text("You can not loan two boards of the same type (lab/home).")
            $("#operation_info").text("Same board type!")
            $("#warning_picture").show()
            decorate_terminate_state(body)

    }

    if (body.state == "valid_student_card") {
            $("#student_name").text(body.student)
            $("#place_board").show()
            $("#scan_card").hide()
            $("#welcome_student").show()
            $("#loaned_lab_board_info").show()
            $("#loaned_lab_board_info").text(body.loaned_lab_board)
            $("#loaned_lab_board_operation").show()
            $("#loaned_lab_board_operation").text(body.loaned_lab_board_operation)
            $("#loaned_home_board_info").show()
            $("#loaned_home_board_info").text(body.loaned_home_board)
            $("#loaned_home_board_operation").show()
            $("#loaned_home_board_operation").text(body.loaned_home_board_operation)
            $("#operation_info").show()
            $("#operation_info").text(body.operation)
    }

    if (body.state == "valid_rfid") {
            $("#student_name").text(body.student)
            $("#place_board").hide()
            $("#scan_card").hide()
            $("#scanned_board_text").show()
            $("#scanned_board_info").show()
            $("#scanned_board_info").text(body.scanned_board)
            $("#operation_info").text(body.operation)
            get_rfid_status()
    }

    if (body.state == "rfid_state_loaned") {
            $("#student_name").text(body.student)
            $("#scanned_board_info").text(body.scanned_board)
            $("#operation_info").text(body.operation)
            $("#return_button_div").show()
            $("#loan_button_div").hide()
    }

    if (body.state == "rfid_state_active") {
            $("#student_name").text(body.student)
            $("#scanned_board_info").text(body.scanned_board)
            $("#operation_info").text(body.operation)
            $("#return_button_div").hide()
            $("#loan_button_div").show()
    }

    if (body.state == "return_error") {
            $("#student_name").text(body.student)
            $("#scanned_board_info").text("You can not return board " + body.scanned_board)
            $("#operation_info").text(body.operation)
            $("#return_button_div").hide()
            $("#loan_button_div").hide()
            $("#warning_picture").show()
            $("#scanned_board_text").hide()
            $("#warning_picture").show()
            decorate_terminate_state(body)
    }

    if (body.state == "loaned") {
            $("#student_name").text(body.student)
            $("#scanned_board_info").text(body.scanned_board + " is successfully assigned on you")
            $("#operation_info").text(body.operation)
            $("#return_button_div").hide()
            $("#loan_button_div").hide()
            $("#scanned_board_text").hide()
            $("#ok_picture").show()
            decorate_success_state(body)
    }

    if (body.state == "returned") {
            $("#student_name").text(body.student)
            $("#scanned_board_info").text(body.scanned_board + " is returned. Place the board at it's numbered place on a shelf.")
            $("#operation_info").text(body.operation)
            $("#return_button_div").hide()
            $("#loan_button_div").hide()
            $("#scanned_board_text").hide()
            $("#ok_picture").show()
            decorate_success_state(body)
    }

}

function refresh_session_state() {
    $.ajax({url: "api/sessions/"+active_session_id,
            method: "GET"})
    .done(handle_session_event)
    .fail(function() {
        clearInterval(session_refresh_timer)
        alert("Timeout/Canceled. Please start again!")
        window.location.replace("/loan")
        })

}


function get_rfid_status() {
    var message = {"type": "get_rfid_status"}
    $.ajax({url: "api/events", method: "POST", data: JSON.stringify(message), dataType: "json"})
}


function session_cancel() {
    var message = {"type": "cancel_button"}
    $.ajax({url: "api/events", method: "POST", data: JSON.stringify(message), dataType: "json"})
}

function session_terminate() {
    var message = {"type": "terminate_button"}
    $.ajax({url: "api/events", method: "POST", data: JSON.stringify(message), dataType: "json"})
}

function session_finish() {
    var message = {"type": "finish_button"}
    $.ajax({url: "api/events", method: "POST", data: JSON.stringify(message), dataType: "json"})
}

function return_scanned_board() {
    var message = {"type": "return_scanned_board_button"}
    $.ajax({url: "api/events", method: "POST", data: JSON.stringify(message), dataType: "json"})
}

function loan_scanned_board() {
    var message = {"type": "loan_scanned_board_button"}
    $.ajax({url: "api/events", method: "POST", data: JSON.stringify(message), dataType: "json"})
}

function session_started(body) {
    console.log("Started session with id " + body.id)
    active_session_id = body.id
    session_refresh_timer = setInterval(refresh_session_state, 1000)
}

$(document).ready(function() {
    console.log("ready!");
    $("#cancel_button").click(session_cancel)
    $("#finish_button").click(session_finish)
    $("#terminate_error_button").click(session_terminate)
    $("#return_button").click(return_scanned_board)
    $("#loan_button").click(loan_scanned_board)
    $.ajax({url: "api/sessions", method: "POST"})
        .done(session_started)
        .fail(function(){
            alert("Active session found. Can not start new session, try again later or finish current session")
            window.location.replace("/loan")
        })
})

