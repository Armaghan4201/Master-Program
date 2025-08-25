import sys
from icecream import ic
import ctypes
import json
import webbrowser

########################################################################
# IMPORT GUI FILE
from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QScrollArea, QSizeGrip
from PySide6.QtCore import QPoint, Signal ,QTimer
from PySide6.QtGui import QAction, QIcon, Qt
from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
from src.ui_interface import Ui_MainWindow

########################################################################
# IMPORT SMT, QR, AND FIRETEST CODES
from src.SMT.smt_handler import SMTHandler
from src.Firetest.firetest_handler import FiretestHandler
from src.QR.qr_handler import QRHandler
from src.messagebox import CustomMessageBox
from src.shortcut_handler import ShortcutHandler
from src.messagebox import CustomMessageBox
########################################################################
## MAIN WINDOW CLASS
########################################################################

USER_DATA_FILE = 'assets/user_data.json'

class MainWindow(QMainWindow):
    login_success_signal = Signal(str, str, str)
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        # self.setWindowIcon(QIcon("assets/Icons/taskbarlogo.jpg"))

        # Remove the title bar and window frame
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        # Initialize the UI as usual
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.shortcut_handler = ShortcutHandler(self)

        scroll_area_style = """
            QScrollArea { 
                border: none;  /* Optional: Removes the border around the scroll area */
            }

            QScrollBar:vertical {
                border: none; 
                background: #212121;  /* Light grey background */
                width: 17px;  /* Width of the vertical scrollbar */
            }

            QScrollBar::handle:vertical {
                border:none;
                background: #676767;  /* Grey color for the handle */
                min-height: 17px;  /* Minimum height of the handle */
            }

            QScrollBar::handle:vertical:hover {
                background: rgb(85, 85, 85);  /* Darker grey when hovered */
            }

            QScrollBar:horizontal {
                border: none; 
                background: #212121;  /* Light grey background */
                height: 17px;  /* Height of the horizontal scrollbar */
            }

            QScrollBar::handle:horizontal {
                  border:none;
                background: #676767; /* Grey color for the handle */
                min-width: 17px;  /* Minimum width of the handle */
            }

            QScrollBar::handle:horizontal:hover {
                background: rgb(85, 85, 85);  /* Darker grey when hovered */
            }

        """
        self.scroll_area = QScrollArea(self)
        
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(scroll_area_style)
        self.ui.side_panel.setFixedWidth(319)

        # Set the central widget of the scroll area to the UI's main content
        self.scroll_area.setWidget(self.ui.centralwidget)
        self.setCentralWidget(self.scroll_area)
        
        # Size grips for edges (top, bottom, left, and right)
        self.size_grip_top_left = QSizeGrip(self)
        self.size_grip_top_right = QSizeGrip(self)
        self.size_grip_bottom_left = QSizeGrip(self)
        self.size_grip_bottom_right = QSizeGrip(self)

        # Set their styles
        for grip in [
            self.size_grip_top_left, self.size_grip_top_right, self.size_grip_bottom_left, self.size_grip_bottom_right
        ]:
          grip.setStyleSheet("""
            background-color: transparent;  /* Transparent background */
            border: none;  /* No border */
            color:transparent;
            image:none;
        """)
          grip.setFixedSize(20,20) 

        #####################################################################
        # APPLY JSON STYLESHEET
        ########################################################################
        loadJsonStyle(self, self.ui, jsonFiles={"json-styles/style.json"}) 
        
        #######################################################################
        self.checkForMissingicons = False
        self.show()

        ########################################################################
        # UPDATE APP SETTINGS LOADED FROM JSON STYLESHEET 
        ########################################################################
        QAppSettings.updateAppSettings(self)

        ########################################################################
        # Custom Code
        ########################################################################

        # # Set Font
        # self.set_font()

        # Navigation stack to track pages
        self.top_bar_height = 37
        self.dragging = False
        self.resizing = False
        self.resize_margin = 10 
        self.offset = QPoint(0,0)
        self.is_maximized = False
        self.navigation_stack = []
        self.side_panel_visible = True
        
        # Connect Top Bar signals
        self.ui.close_pushButton.clicked.connect(self.close_window)
        self.ui.minimize_pushButton.clicked.connect(self.minus_window)
        self.ui.maximize_pushButton.clicked.connect(self.toggle_maximize)
        self.ui.back_pushButton.clicked.connect(self.go_back)

        self.open_at_shorter_size()

        # Call Login And Register Methods here.
        self.login_and_registration_setup()
        self.ui.Whole_front_stack_Widget.setCurrentWidget(self.ui.login_registration_password_page)
        self.show_login_page()

        self.current_prompt = None
        self.login_success_signal.connect(self.connect_all_signals)

        # Add the User Menu
        self.setup_user_menu()

    def open_at_shorter_size(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        window_width = int(screen_width * 0.6)
        window_height = int(screen_height * 0.8)
        self.resize(window_width, window_height)
        self.move((screen_width - window_width) // 2, (screen_height - window_height) // 2)

    def resizeEvent(self, event):
        """Position size grips in all four corners."""
        margin = 2  # Margin from the window edges
       
        # Place corner grips using setGeometry (x, y, width, height)
        self.size_grip_bottom_right.setGeometry(
            self.width() - self.size_grip_bottom_right.width() - margin,
            self.height() - self.size_grip_bottom_right.height() - margin,
            self.size_grip_bottom_right.width(),
            self.size_grip_bottom_right.height()
        )
        self.size_grip_bottom_left.setGeometry(
            margin,
            self.height() - self.size_grip_bottom_left.height() - margin,
            self.size_grip_bottom_left.width(),
            self.size_grip_bottom_left.height()
        )
        self.size_grip_top_right.setGeometry(
            self.width() - self.size_grip_top_right.width() - margin,
            margin,
            self.size_grip_top_right.width(),
            self.size_grip_top_right.height()
        )
        self.size_grip_top_left.setGeometry(
            margin,
            margin,
            self.size_grip_top_left.width(),
            self.size_grip_top_left.height()
        )

        self.setMinimumSize(20, 20) 
        super(MainWindow, self).resizeEvent(event)


    def toggle_sidepanel(self):
        """Smoothly toggle the side panel to hide or show with a faster transition and change the button icon."""
        
        # Define the widths
        collapsed_width = 0  # When hidden
        expanded_width = 319  # When visible

        # Get the current width of the side panel
        current_width = self.ui.side_panel.width()

        # Handle the initial state if it's the first click
        if current_width == 0:
            # Set the side panel directly to expanded width
            self.ui.side_panel.setFixedWidth(expanded_width)
            self.ui.toggle_pushButton.setIcon(QIcon("Qss/icons/Icons/feather/chevron-left.png"))
            return

        # Check the current state and determine the target state
        if current_width == expanded_width:
            # Collapse the side panel
            target_width = collapsed_width
            new_icon = "Qss/icons/Icons/feather/align-justify.png"  # Icon for collapsed state
        else:
            # Expand the side panel
            target_width = expanded_width
            new_icon = "Qss/icons/Icons/feather/chevron-left.png"  # Icon for expanded state

        # Step size for faster transition
        step_size = 30  # Increased for faster transition
        direction = 1 if target_width > current_width else -1  # Determine the direction of resizing

        # Function to smoothly resize the side panel
        def resize_panel():
            nonlocal current_width
            if direction == 1 and current_width < target_width:
                current_width = min(current_width + step_size, target_width)  # Ensure it doesn't exceed target width
            elif direction == -1 and current_width > target_width:
                current_width = max(current_width - step_size, target_width)  # Ensure it doesn't go below target width
            else:
                # Stop the timer when the target width is reached
                self.ui.toggle_pushButton.setIcon(QIcon(new_icon))
                return False

            # Adjust the side panel's width
            self.ui.side_panel.setFixedWidth(current_width)
            return True

        # Start the resizing transition using a timer
        def repeat_resize():
            if resize_panel():
                QTimer.singleShot(1, repeat_resize)  # Reduced interval for faster animation

        # Begin the repeat resizing
        repeat_resize()


    def setup_user_menu(self):
        self.ui.usermenu_pushButton.clicked.connect(lambda: self.show_user_menu(self.ui.usermenu_pushButton))
        self.ui.usermenu_pushButton_2.clicked.connect(lambda: self.show_user_menu(self.ui.usermenu_pushButton_2))
        self.ui.usermenu_pushButton_3.clicked.connect(lambda: self.show_user_menu(self.ui.usermenu_pushButton_3))
        self.ui.usermenu_pushButton_4.clicked.connect(lambda: self.show_user_menu(self.ui.usermenu_pushButton_4))
        self.ui.usermenu_pushButton_5.clicked.connect(lambda: self.show_user_menu(self.ui.usermenu_pushButton_5))
        self.ui.usermenu_pushButton_6.clicked.connect(lambda: self.show_user_menu(self.ui.usermenu_pushButton_6))
        self.ui.usermenu_pushButton_7.clicked.connect(lambda: self.show_user_menu(self.ui.usermenu_pushButton_7))
        
        # Define the user menu
        self.user_menu = QMenu(self)
        self.user_menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e1e;  /* Darker background for modern look */
                color: white;  /* Text color */
                border: 2px solid #3c3f41;  /* Subtle border to match dark theme */
                border-radius: 8px;  /* Smooth rounded corners */
                padding: 5px;  /* Internal spacing for the menu */
                box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.3);  /* Shadow for depth */
            }
            QMenu::item {
                padding: 10px 20px;  /* Space around each menu item */
                margin: 2px;  /* Space between items */
                border-radius: 5px;  /* Rounded corners for each item */
                background-color: transparent;  /* Default transparent background */
                color: #e0e0e0;  /* Slightly lighter text for visibility */
                cursor: pointer;
            }
            QMenu::item:selected {
                background-color: #424242;  /* Highlight color for selected item */
                color: white;  /* Text color for selected item */
                cursor: pointer;
            }
            QMenu::separator {
                height: 1px;  /* Thin separator line */
                background: #3c3f41;  /* Separator color */
                margin: 5px 10px;  /* Spacing around separator */
            }
        """)

        # Add actions to the menu
        self.action_profile = QAction("View Profile", self)
        self.action_about = QAction("About", self)
        self.action_logout = QAction("Logout", self)

        self.user_menu.addAction(self.action_profile)
        self.user_menu.addAction(self.action_about)
        self.user_menu.addSeparator()  # Add a horizontal line (separator)
        self.user_menu.addAction(self.action_logout)

        # Connect menu actions
        self.action_logout.triggered.connect(self.logout_user)
        self.action_about.triggered.connect(self.show_about_page)
        self.action_profile.triggered.connect(self.show_user_profile)
    

    def show_user_menu(self, usermenu_button):
        # Show the menu slightly to the left and above the profile button
        button_pos = usermenu_button.mapToGlobal(
            QPoint(-90, usermenu_button.height() +3)  # Adjust y-offset for upward shift
        )
        self.user_menu.move(button_pos)
        self.user_menu.show()


    def connect_all_signals(self, username, code, designation):
        self.ui.home_page_stackedWidget.currentChanged.connect(self.track_page)
        self.ui.developed_by_softdev_pushButton.clicked.connect(self.open_gmail)
        self.ui.developed_by_softdev_pushButton_2.clicked.connect(self.open_gmail)
        self.ui.developed_by_softdev_pushButton_3.clicked.connect(self.open_gmail)
        self.ui.developed_by_softdev_pushButton_5.clicked.connect(self.open_gmail)
        self.ui.developed_by_softdev_pushButton_6.clicked.connect(self.open_gmail)
        self.ui.developed_by_softdev_pushButton_7.clicked.connect(self.open_gmail)
        self.ui.toggle_pushButton.clicked.connect(self.toggle_sidepanel)

        # Update Program Name whenever a page is switched
        self.ui.home_page_stackedWidget.currentChanged.connect(self.program_name_update)
        self.ui.smt_stackedWidget.currentChanged.connect(self.program_name_update)
        self.ui.qr_stackedWidget.currentChanged.connect(self.program_name_update)
        self.ui.firetest_stackedWidget.currentChanged.connect(self.program_name_update)
        self.ui.profile_stackedWidget.currentChanged.connect(self.program_name_update)

        # Open the home page after Successfully Logging In
        self.ui.Whole_front_stack_Widget.setCurrentWidget(self.ui.home_page)
        self.ui.home_page_stackedWidget.setCurrentWidget(self.ui.SMT_page)

        # Set user details
        self.username = username
        self.code = code
        self.designation = designation

        # Initialize handlers
        self.smt_handler = SMTHandler(self.ui)
        self.firetest_handler = FiretestHandler(self.ui)
        self.qr_handler = QRHandler(self.ui, username=self.username, user_code=self.code, user_designation=self.designation) 

        self.connect_side_panel_signals()
        self.smt_handler.connect_smt_signals()
        self.firetest_handler.connect_firetest_signals()
        self.qr_handler.connect_qr_signals()
        
        # Connect signals for side panel buttons
        self.setup_side_panel_buttons()
         
        # Connect Firetest button to navigate and toggle side panel
        self.ui.firetest_pushButton.clicked.connect(self.open_firetest_page_and_toggle)

        # Connect Profile Page Buttons
        self.ui.change_password_pushButton.clicked.connect(self.show_change_password_page)
        self.ui.forgetyourpassword_pushButton.clicked.connect(self.show_change_password_page)
        self.ui.update_password_pushButton.clicked.connect(self.update_password)
        self.ui.cancel_update_password_pushButton.clicked.connect(self.show_user_profile)

    def open_firetest_page_and_toggle(self):
        """Navigate to the firetest page and toggle the side panel."""
        # Navigate to the firetest page
        self.toggle_sidepanel()
        self.ui.home_page_stackedWidget.setCurrentWidget(self.ui.Firetest_page)


    def setup_side_panel_buttons(self):
    # Styles
        active_style = """
            QPushButton {
                text-align: left;              
                padding-top: 9px;       
                width : 270;
                height: 40;     
                padding-bottom: 9px;         
                border-radius: 10px; 
                padding-left:12px;           
                border: none;                  
                background-color: #2F2F2F; 
                color: white;
            }
            QPushButton:hover {
                background-color: #212121; /* Slightly lighter hover color for active */
                color: white;
                font: bold;
            }
        """
        inactive_style = """
            QPushButton {
                text-align: left;              
                padding-top: 9px; 
                width : 270;
                height: 40;
                padding-left:12px;           
                padding-bottom: 9px;         
                border-radius: 10px;           
                border: none;                  
                background-color: transparent; 
                color: white;
            }
            QPushButton:hover {
                background-color: #212121; /* Hover effect for inactive */
                color: white;
                font: bold;
            }
        """
        # List of side panel buttons
        self.side_panel_buttons = [
            self.ui.smt_pushButton,
            self.ui.firetest_pushButton,
            self.ui.about_pushButton,
            self.ui.qr_pushButton,
            self.ui.profile_pushButton
        ]

        # Set all buttons as checkable
        for button in self.side_panel_buttons:
            button.setCheckable(True)

        # Connect each button to the slot
        for button in self.side_panel_buttons:
            button.clicked.connect(lambda _, b=button: self.set_active_button(b, active_style, inactive_style))
        # Set default active button
        self.set_active_button(self.ui.smt_pushButton, active_style, inactive_style)

    def set_active_button(self, active_button, active_style, inactive_style):
        # Reset styles for all buttons
        for button in self.side_panel_buttons:
            button.setStyleSheet(inactive_style)  # Apply inactive style

        # Set active style for the clicked button
        active_button.setStyleSheet(active_style)

    def login_and_registration_setup(self):
        self.ui.login_page_button_in_login.clicked.connect(self.show_login_page)
        self.ui.register_page_button_in_login.clicked.connect(self.show_register_page)
        self.ui.register_page_button_in_login_2.clicked.connect(self.show_register_page)
        self.ui.login_button.clicked.connect(self.login)

        # Register Page # Connect to register method
        self.ui.login_page_button_in_register.clicked.connect(self.show_login_page)
        self.ui.login_page_button_in_register_2.clicked.connect(self.show_login_page)
        self.ui.register_page_button_in_register.clicked.connect(self.show_register_page)
        self.ui.register_button.clicked.connect(self.register)

    def show_login_page(self):
        self.ui.login_line_edit.setText("")
        self.ui.login_registration_password_stackedWidget.setCurrentWidget(self.ui.login_page)

    def show_register_page(self):
        self.ui.register_enter_username.setText("")
        self.ui.register_enter_4_digit_code.setText("")
        self.ui.operator_radioButton.setChecked(False)
        self.ui.engineer_radioButton.setChecked(False)
        self.ui.login_registration_password_stackedWidget.setCurrentIndex(1)

    def register(self):
        username = self.ui.register_enter_username.text()
        code = self.ui.register_enter_4_digit_code.text()
        operator = self.ui.operator_radioButton.isChecked()
        engineer = self.ui.engineer_radioButton.isChecked()

        # Check if username or code is invalid or if neither radio button is checked
        if not username or len(code) != 4 or not code.isdigit() or not (engineer or operator):
            CustomMessageBox.show_message(self, "Invalid Input", "Please fill all the fields correctly.", QtWidgets.QMessageBox.Critical)
            self.show_register_page()
            return

        try:
            with open(USER_DATA_FILE, 'r') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {}

        if username in self.users:
            CustomMessageBox.show_message(self, "Registration Error", "User already exists. Please choose a different name.", QtWidgets.QMessageBox.Critical)
            self.show_register_page()
            return
        
        # Check if the code is already used by another user
        if any(user['code'] == code for user in self.users.values()):
            CustomMessageBox.show_message(self, "Registration Error", "4-digit Code already in use. Please enter a unique code.", QtWidgets.QMessageBox.Critical)
            self.show_register_page()
            return
        
        # Assign designation based on the radio button checked
        designation = "Engineer" if engineer else "Operator"
        self.users[username] = {'designation': designation, 'code': code}
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(self.users, f)

        CustomMessageBox.show_message(self, "Registration Successful", "User registered successfully!", QtWidgets.QMessageBox.Information)
        self.show_login_page()

    def login(self):
        code = self.ui.login_line_edit.text()
        # Validate input
        if len(code) != 4 or not code.isdigit():
            CustomMessageBox.show_message(self, "Invalid Input", "The code must be a 4-digit number.", QtWidgets.QMessageBox.Icon.Critical)
            self.show_login_page()
            return

        # Try to load user data
        try:
            with open(USER_DATA_FILE, 'r') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            CustomMessageBox.show_message(self, "Login Failed", "No registered users found.", QtWidgets.QMessageBox.Icon.Critical)
            return

        # Check the entered code against stored users
        for username, details in self.users.items():
            if details['code'] == code:
                self.username = username
                self.code = code
                self.designation = details['designation']
                self.ui.smt_stackedWidget.setCurrentWidget(self.ui.file_uploading_page_in_smt)
                self.login_success_signal.emit(username, code, details['designation'])  # Emit login success signal
                self.ui.login_line_edit.setText("")
                
                split_username = self.username.split(" ")
                if len(split_username) == 1:
                    self.ui.usermenu_pushButton.setText(self.username[0][0])
                    self.ui.usermenu_pushButton_2.setText(self.username[0][0])
                    self.ui.usermenu_pushButton_3.setText(self.username[0][0])
                    self.ui.usermenu_pushButton_4.setText(self.username[0][0])
                    self.ui.usermenu_pushButton_5.setText(self.username[0][0])
                    self.ui.usermenu_pushButton_6.setText(self.username[0][0])
                    self.ui.usermenu_pushButton_7.setText(self.username[0][0])
                    self.ui.profilepushButton_in_profile.setText(self.username[0][0])
                elif len(split_username) == 2:
                    self.ui.usermenu_pushButton.setText(split_username[0][0] + split_username[1][0])
                    self.ui.usermenu_pushButton_2.setText(split_username[0][0] + split_username[1][0])
                    self.ui.usermenu_pushButton_3.setText(split_username[0][0] + split_username[1][0])
                    self.ui.usermenu_pushButton_4.setText(split_username[0][0] + split_username[1][0])
                    self.ui.usermenu_pushButton_5.setText(split_username[0][0] + split_username[1][0])
                    self.ui.usermenu_pushButton_6.setText(split_username[0][0] + split_username[1][0])
                    self.ui.usermenu_pushButton_7.setText(split_username[0][0] + split_username[1][0])
                    self.ui.profilepushButton_in_profile.setText(split_username[0][0] + split_username[1][0])
                return

        # If no match found
        CustomMessageBox.show_message(self, "Login Failed", "Incorrect code or User not found.", QtWidgets.QMessageBox.Icon.Critical)
        self.show_login_page()

    def logout_user(self):
        self.ui.Whole_front_stack_Widget.setCurrentWidget(self.ui.login_registration_password_page)
        self.ui.login_registration_password_stackedWidget.setCurrentWidget(self.ui.login_page)

    def update_password(self):
        new_password = self.ui.new_password_lineedit.text()
        confirmed_new_password = self.ui.confirm_password_lineedit.text()
        
        if new_password != confirmed_new_password:
            CustomMessageBox.show_message(self.ui.centralwidget, "Passwords Not Matching", "The entered passwords do not match", QtWidgets.QMessageBox.Icon.Critical)
            self.show_change_password_page()
            return
        
        if len(new_password) != 4 or not new_password.isdigit():
            CustomMessageBox.show_message(self.ui.centralwidget, "Incorrect Password", "The entered password must be a 4 digit code", QtWidgets.QMessageBox.Icon.Critical)
            self.show_change_password_page()
            return
        
        self.code = new_password
        self.users[self.username] = {'designation': self.designation, 'code': self.code}
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(self.users, f)

        CustomMessageBox.show_message(self, "Password Change Successful", "Password changed successfully!", QtWidgets.QMessageBox.Icon.Information)
        self.show_user_profile()

    def connect_side_panel_signals(self):
        self.ui.smt_pushButton.clicked.connect(self.smt_pushButton_handling)
        self.ui.qr_pushButton.clicked.connect(self.qr_pushButton_handling)
        self.ui.firetest_pushButton.clicked.connect(self.firetest_pushButton_handling)
        self.ui.logout_in_sidepanel_pushButton.clicked.connect(self.logout_user)
        self.ui.about_pushButton.clicked.connect(self.show_about_page)
        self.ui.profile_pushButton.clicked.connect(self.show_user_profile)

    def show_user_profile(self):
        self.ui.username_lineEdit_in_profile.setText(self.username)
        self.ui.designation_lineEdit.setText(self.designation)
        self.ui.password_lineEdit_in_profile.setText(self.code)
        
        self.ui.home_page_stackedWidget.setCurrentWidget(self.ui.profile_page)
        self.ui.profile_stackedWidget.setCurrentWidget(self.ui.profile_page_save)

    def show_change_password_page(self):
        self.ui.new_password_lineedit.clear()
        self.ui.confirm_password_lineedit.clear()
        self.ui.profile_stackedWidget.setCurrentWidget(self.ui.newpassword_page)

    def show_about_page(self):
        self.ui.home_page_stackedWidget.setCurrentWidget(self.ui.About_page)

    def smt_pushButton_handling(self):
        self.ui.choose_file_pushButton_in_smt.setText("Choose file")
        self.ui.drag_drop_label.setText("to upload or Drag & Drop")
        self.ui.select_only_txt_label.setText("Select only .txt file")
        self.ui.folder_path_lineEdit.clear()

        self.ui.home_page_stackedWidget.setCurrentWidget(self.ui.SMT_page)
        self.ui.smt_stackedWidget.setCurrentWidget(self.ui.file_uploading_page_in_smt)

    def qr_pushButton_handling(self):
        self.ui.enter_mo_lineEdit.clear()
        self.ui.dielectric_option_dropdown.clear()
        self.ui.bbo_option_dropdown.clear()
        self.ui.program_no_lineEdit.clear()
        self.ui.kiln_dropdown.clear()

        self.ui.home_page_stackedWidget.setCurrentWidget(self.ui.QR_page)
        if self.designation=="Engineer":
            self.qr_handler.create_qr_code()
        else:
            self.qr_handler.show_enter_qr_code_data_page()

    def firetest_pushButton_handling(self):
        self.ui.home_page_stackedWidget.setCurrentWidget(self.ui.Firetest_page)
        self.firetest_handler.open_single_test_page()

    def program_name_update(self):
        # If SMT
        if self.ui.home_page_stackedWidget.currentWidget() == self.ui.SMT_page:
            self.ui.current_program_name_label.setText("SMT")
            if self.ui.smt_stackedWidget.currentIndex() <= 2:
                self.ui.current_program_detail_label.setText("Design Automation")
            else:
                self.ui.current_program_detail_label.setText("Buildsheet Automation")
        
        # If QR
        if self.ui.home_page_stackedWidget.currentWidget() == self.ui.QR_page:
            self.ui.current_program_name_label.setText("QR")
            if self.ui.qr_stackedWidget.currentWidget() == self.ui.enter_qr_data_page:
                self.ui.current_program_detail_label.setText("QR Codes Comparison")
            else:
                self.ui.current_program_detail_label.setText("QR Code Generation")
        
        # If FireTest
        if self.ui.home_page_stackedWidget.currentWidget() == self.ui.Firetest_page:
            self.ui.current_program_name_label.setText("FireTest")
            if self.ui.firetest_stackedWidget.currentWidget() == self.ui.batch_test_page:
                self.ui.current_program_detail_label.setText("Batch Testing")
            else:
                self.ui.current_program_detail_label.setText("Single Testing")
                
        # If About Page
        if self.ui.home_page_stackedWidget.currentWidget() == self.ui.About_page:
            self.ui.current_program_name_label.setText("About")
            self.ui.current_program_detail_label.clear()
                
        # If Profile Page
        if self.ui.home_page_stackedWidget.currentWidget() == self.ui.profile_page:
            self.ui.current_program_name_label.setText("User Profile")
            self.ui.current_program_detail_label.clear()

    def set_font(self):
        # Load the Lato font
        font_id = QtGui.QFontDatabase.addApplicationFont("assets/Lato/Lato-Regular.ttf")
        if font_id == -1:
            CustomMessageBox.show_message(
                self,
                "Font Failure",
                "Failed to Load Lato Font",
                QtWidgets.QMessageBox.Critical
            )
        else:
            font_family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0]
            app_font = QtGui.QFont(font_family)
            QtWidgets.QApplication.instance().setFont(app_font)

    def mousePressEvent(self, event):
        """Handle mouse press for dragging the window."""
        if event.button() == Qt.LeftButton:
            # Check if the cursor is inside the top bar
            if event.pos().y() <= self.top_bar_height:
                if self.isMaximized():
                    # Calculate the relative position before restoring
                    relative_x = event.globalPosition().x() / self.width()
                    relative_y = event.globalPosition().y() / self.height()

                    # Restore the window to normal size
                    self.showNormal()

                    # Adjust the offset after restoring
                    new_width = self.width()
                    new_height = self.height()
                    self.offset = QPoint(relative_x * new_width, relative_y * new_height)
                else:
                    self.offset = event.globalPosition().toPoint() - self.pos()

                self.dragging = True
                event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse movement for dragging the window."""
        if self.dragging:
            # Only move the window if dragging is enabled
            new_pos = event.globalPosition().toPoint() - self.offset
            self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop dragging."""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

    
    def track_page(self, index):
        if self.navigation_stack and self.navigation_stack[-1] == index:
            return
        self.navigation_stack.append(index)
        self.dragging = False
        self.resizing = False

    def go_back(self):
        """Navigate to the previous page or handle navigation within nested stacked widgets."""
        # Get the current index of the main stacked widget
        whole_widget = self.ui.Whole_front_stack_Widget.currentWidget()

        # If on the fourth page (home_page_stackedWidget)
        if whole_widget == self.ui.home_page:
            if len(self.navigation_stack) > 1:
                # Remove the current page from history
                self.navigation_stack.pop()
                # Get the last visited page
                last_page_index = self.navigation_stack[-1]
                self.ui.home_page_stackedWidget.setCurrentIndex(last_page_index)
            
        else:
            # General navigation for other pages in the main stacked widget
            if whole_widget == self.ui.login_page:
                self.ui.Whole_front_stack_Widget.setCurrentWidget(self.ui.registration_page)

            elif whole_widget == self.ui.registration_page:
                self.ui.Whole_front_stack_Widget.setCurrentWidget(self.ui.login_page)


    def close_window(self):
        """Close the application."""
        self.close()
        sys.exit()

    def toggle_maximize(self):
        """Toggle between maximized and normal state."""
        if self.is_maximized:
            self.showNormal()  # Restore to normal size
            self.is_maximized = False
        else:
            self.showMaximized()  # Maximize the window
            self.is_maximized = True

    def minus_window(self):
        """Minimize the application."""
        self.showMinimized()

    def open_gmail(self):
        gmail_url = "https://mail.google.com/mail/u/0/?fs=1&to=nashitsaleem9@gmail.com&su=YourSubject&body=YourMessage&tf=cm"
        webbrowser.open(gmail_url)

########################################################################
## EXECUTE APP
########################################################################
if __name__ == "__main__":
    
    # Create the QApplication instance before any QWidget is created
    app = QApplication(sys.argv)
    myappid = 'com.softdev.desktop_app.main.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app.setWindowIcon(QIcon("Qss/icons/Icons/custom/taskbarlogo.jpg"))

    # Create the main window and show it
    window = MainWindow()
    window.show()

    # Start the application event loop
    sys.exit(app.exec())