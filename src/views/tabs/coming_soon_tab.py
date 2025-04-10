"""
Coming Soon Tab Module

This module provides a placeholder interface for features that are currently in development.
"""

import datetime
import json
import os
from PySide6.QtCore import Qt, Slot, QUrl
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QFormLayout, QLineEdit, 
    QTextEdit, QGroupBox, QHeaderView, QDateEdit, QSizePolicy,
    QMessageBox, QCheckBox, QDialog, QDialogButtonBox
)
from PySide6.QtGui import QDesktopServices

from src.utils.logger import Logger
from src.models.app_state import AppState
from src.utils.settings_manager import SettingsManager
from src.utils.ui_theme import (
    get_group_box_style, get_label_style, get_button_style,
    get_form_input_label_style, get_text_edit_style, get_line_edit_style,
    get_table_style, get_checkbox_style, get_message_box_style,
    get_dialog_background_style, get_status_background_color, get_status_text_color,
    PRIMARY_COLOR, SECONDARY_COLOR, TEXT_PRIMARY
)

class ComingSoonTab(QWidget):
    """
    Coming Soon Tab to display features that are in development
    and allow users to submit feedback.
    """
    
    def __init__(self, parent=None):
        super(ComingSoonTab, self).__init__(parent)
        
        # Get singleton instances
        self.logger = Logger.instance()
        self.app_state = AppState.instance()
        self.settings_manager = SettingsManager.instance()
        
        # Set up the UI
        self._setup_ui()
        
        # Load saved features
        self._load_features()
        
        self.logger.debug("ComingSoonTab initialized")
    
    def _setup_ui(self):
        """Set up the user interface for the coming soon tab"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Create title section
        title_group = QGroupBox("Coming Soon Features")
        title_group.setStyleSheet(get_group_box_style(is_title_centered=True))
        title_layout = QVBoxLayout(title_group)
        
        description = QLabel(
            "This page shows upcoming features for the Tennis Ball Tracker application. "
            "You can also submit feedback or feature requests below."
        )
        description.setWordWrap(True)
        description.setStyleSheet(get_label_style(is_description=True))
        description.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(description)
        
        self.layout.addWidget(title_group)
        
        # Create content layout with 70/30 split
        content_layout = QHBoxLayout()
        
        # Left side: Features table (70%)
        feature_buttons_layout = self._setup_features_table()
        features_group = QGroupBox("Upcoming Features")
        features_group.setStyleSheet(get_group_box_style())
        features_layout = QVBoxLayout(features_group)
        features_layout.addWidget(self.features_table)
        features_layout.addLayout(feature_buttons_layout)
        content_layout.addWidget(features_group, 70)
        
        # Right side: Feedback form (30%)
        self._setup_feedback_form()
        feedback_group = QGroupBox("")
        feedback_group.setStyleSheet(get_group_box_style())
        feedback_layout = QVBoxLayout(feedback_group)
        feedback_layout.addLayout(self.feedback_form)
        
        # Add submit button to feedback form
        self.submit_button = QPushButton("Submit Feedback")
        self.submit_button.setStyleSheet(get_button_style(is_primary=True))
        self.submit_button.clicked.connect(self._submit_feedback)
        feedback_layout.addWidget(self.submit_button)
        
        # Add reset button
        self.reset_button = QPushButton("Reset Form")
        self.reset_button.setStyleSheet(get_button_style())
        self.reset_button.clicked.connect(self._reset_form)
        feedback_layout.addWidget(self.reset_button)
        
        content_layout.addWidget(feedback_group, 30)
        
        # Add content layout to main layout
        self.layout.addLayout(content_layout)
        
        # Add resources section at the bottom
        resources_group = QGroupBox("Additional Resources")
        resources_group.setStyleSheet(get_group_box_style())
        resources_layout = QVBoxLayout(resources_group)
        
        resources_description = QLabel(
            "Check out these resources for more information about the Tennis Ball Tracker project:"
        )
        resources_description.setWordWrap(True)
        resources_description.setStyleSheet(get_label_style())
        resources_layout.addWidget(resources_description)
        
        # Resources buttons layout
        resources_buttons = QHBoxLayout()
        
        # Documentation button
        docs_button = QPushButton("Documentation")
        docs_button.setStyleSheet(get_button_style())
        docs_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://pk2381.pythonanywhere.com/animation/underconstruction/")))
        resources_buttons.addWidget(docs_button)
        
        # GitHub button
        github_button = QPushButton("GitHub Repository")
        github_button.setStyleSheet(get_button_style())
        github_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://pk2381.pythonanywhere.com/animation/underconstruction/")))
        resources_buttons.addWidget(github_button)
        
        # Support button
        support_button = QPushButton("Support")
        support_button.setStyleSheet(get_button_style())
        support_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://pk2381.pythonanywhere.com/animation/underconstruction/")))
        resources_buttons.addWidget(support_button)
        
        resources_layout.addLayout(resources_buttons)
        self.layout.addWidget(resources_group)
        
    def _setup_features_table(self):
        """Set up the features table"""
        self.features_table = QTableWidget(0, 4)
        self.features_table.setStyleSheet(get_table_style())
        
        # Set headers
        self.features_table.setHorizontalHeaderLabels(["Feature", "Description", "Version", "Status"])
        
        # Set header properties
        header = self.features_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        # Add feature management buttons
        feature_buttons_layout = QHBoxLayout()
        
        self.add_feature_button = QPushButton("Add Feature")
        self.add_feature_button.setStyleSheet(get_button_style(is_primary=True))
        self.add_feature_button.clicked.connect(self._add_feature_dialog)
        feature_buttons_layout.addWidget(self.add_feature_button)
        
        self.edit_feature_button = QPushButton("Edit Feature")
        self.edit_feature_button.setStyleSheet(get_button_style())
        self.edit_feature_button.clicked.connect(self._edit_feature_dialog)
        feature_buttons_layout.addWidget(self.edit_feature_button)
        
        self.delete_feature_button = QPushButton("Delete Feature")
        self.delete_feature_button.setStyleSheet(get_button_style())
        self.delete_feature_button.clicked.connect(self._delete_feature)
        feature_buttons_layout.addWidget(self.delete_feature_button)
        
        # Add save button
        self.save_button = QPushButton("Save Features")
        self.save_button.setStyleSheet(get_button_style(is_primary=True))
        self.save_button.clicked.connect(self._save_features)
        feature_buttons_layout.addWidget(self.save_button)
        
        # Return the feature buttons layout to be added to the features group
        return feature_buttons_layout

    def _add_feature(self, name, description, version, implemented=False):
        """Add a feature to the table"""
        row = self.features_table.rowCount()
        self.features_table.insertRow(row)
        
        # Create and add table items
        name_item = QTableWidgetItem(name)
        name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.features_table.setItem(row, 0, name_item)
        
        desc_item = QTableWidgetItem(description)
        desc_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.features_table.setItem(row, 1, desc_item)
        
        version_item = QTableWidgetItem(version)
        version_item.setTextAlignment(Qt.AlignCenter)
        self.features_table.setItem(row, 2, version_item)
        
        status_text = "Implemented" if implemented else "Coming Soon"
        status_item = QTableWidgetItem(status_text)
        status_item.setTextAlignment(Qt.AlignCenter)
        
        # Set background and text color based on status
        status_item.setBackground(get_status_background_color(implemented))
        status_item.setForeground(get_status_text_color())
            
        self.features_table.setItem(row, 3, status_item)
    
    def _setup_feedback_form(self):
        """Set up the feedback form"""
        self.feedback_form = QFormLayout()
        self.feedback_form.setSpacing(10)
        
        # Name field
        name_label = QLabel("Name:")
        name_label.setStyleSheet(get_form_input_label_style())
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(get_line_edit_style())
        self.name_input.setPlaceholderText("Your name")
        self.feedback_form.addRow(name_label, self.name_input)
        
        # Email field
        email_label = QLabel("Email:")
        email_label.setStyleSheet(get_form_input_label_style())
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet(get_line_edit_style())
        self.email_input.setPlaceholderText("Your email address")
        self.feedback_form.addRow(email_label, self.email_input)
        
        # Feedback type
        feedback_type_label = QLabel("Feedback Type:")
        feedback_type_label.setStyleSheet(get_form_input_label_style())
        
        # Create checkboxes in a container
        feedback_type_container = QWidget()
        feedback_type_layout = QVBoxLayout(feedback_type_container)
        feedback_type_layout.setContentsMargins(0, 0, 0, 0)
        feedback_type_layout.setSpacing(5)
        
        self.feature_request_checkbox = QCheckBox("Feature Request")
        self.feature_request_checkbox.setStyleSheet(get_checkbox_style())
        feedback_type_layout.addWidget(self.feature_request_checkbox)
        
        self.bug_report_checkbox = QCheckBox("Bug Report")
        self.bug_report_checkbox.setStyleSheet(get_checkbox_style())
        feedback_type_layout.addWidget(self.bug_report_checkbox)
        
        self.improvement_checkbox = QCheckBox("Improvement Suggestion")
        self.improvement_checkbox.setStyleSheet(get_checkbox_style())
        feedback_type_layout.addWidget(self.improvement_checkbox)
        
        self.feedback_form.addRow(feedback_type_label, feedback_type_container)
        
        # Feedback content
        feedback_label = QLabel("Feedback:")
        feedback_label.setStyleSheet(get_form_input_label_style())
        self.feedback_input = QTextEdit()
        self.feedback_input.setStyleSheet(get_text_edit_style())
        self.feedback_input.setPlaceholderText("Please describe your feedback, feature request or issue in detail")
        self.feedback_input.setMinimumHeight(150)
        self.feedback_form.addRow(feedback_label, self.feedback_input)
        
    def _submit_feedback(self):
        """Handle feedback submission"""
        # Check if required fields are filled
        if not self.name_input.text() or not self.email_input.text() or not self.feedback_input.toPlainText():
            message_box = QMessageBox()
            message_box.setStyleSheet(get_message_box_style())
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Missing Information")
            message_box.setText("Please fill in all required fields (Name, Email, and Feedback).")
            message_box.exec()
            return
        
        # Check if at least one feedback type is selected
        if not (self.feature_request_checkbox.isChecked() or 
                self.bug_report_checkbox.isChecked() or 
                self.improvement_checkbox.isChecked()):
            message_box = QMessageBox()
            message_box.setStyleSheet(get_message_box_style())
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Missing Information")
            message_box.setText("Please select at least one feedback type.")
            message_box.exec()
            return
        
        # In a real application, this would submit the data to a server
        # For now, just show a success message and reset the form
        self.logger.info(f"Feedback submitted by {self.name_input.text()}")
        
        message_box = QMessageBox()
        message_box.setStyleSheet(get_message_box_style())
        message_box.setIcon(QMessageBox.Information)
        message_box.setWindowTitle("Feedback Submitted")
        message_box.setText("Thank you for your feedback! Your input helps us improve the application.")
        message_box.exec()
        
        # Reset the form
        self._reset_form()
        
    def _reset_form(self):
        """Reset the feedback form"""
        self.name_input.clear()
        self.email_input.clear()
        self.feature_request_checkbox.setChecked(False)
        self.bug_report_checkbox.setChecked(False)
        self.improvement_checkbox.setChecked(False)
        self.feedback_input.clear()
        
    def _add_feature_dialog(self):
        """Show dialog to add a new feature"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Feature")
        dialog.setStyleSheet(get_dialog_background_style())
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Create form layout
        form = QFormLayout()
        form.setSpacing(10)
        
        # Feature name field
        name_label = QLabel("Feature Name:")
        name_label.setStyleSheet(get_form_input_label_style())
        self.new_feature_name = QLineEdit()
        self.new_feature_name.setStyleSheet(get_line_edit_style())
        self.new_feature_name.setPlaceholderText("Enter feature name")
        form.addRow(name_label, self.new_feature_name)
        
        # Description field
        desc_label = QLabel("Description:")
        desc_label.setStyleSheet(get_form_input_label_style())
        self.new_feature_desc = QTextEdit()
        self.new_feature_desc.setStyleSheet(get_text_edit_style())
        self.new_feature_desc.setPlaceholderText("Enter feature description")
        self.new_feature_desc.setMinimumHeight(100)
        form.addRow(desc_label, self.new_feature_desc)
        
        # Version field
        version_label = QLabel("Version:")
        version_label.setStyleSheet(get_form_input_label_style())
        self.new_feature_version = QLineEdit()
        self.new_feature_version.setStyleSheet(get_line_edit_style())
        self.new_feature_version.setPlaceholderText("e.g., v1.0")
        form.addRow(version_label, self.new_feature_version)
        
        # Implemented status
        status_label = QLabel("Status:")
        status_label.setStyleSheet(get_form_input_label_style())
        self.new_feature_implemented = QCheckBox("Implemented")
        self.new_feature_implemented.setStyleSheet(get_checkbox_style())
        form.addRow(status_label, self.new_feature_implemented)
        
        layout.addLayout(form)
        
        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self._save_new_feature(dialog))
        button_box.rejected.connect(dialog.reject)
        
        # Style the buttons
        for button in button_box.buttons():
            if button_box.buttonRole(button) == QDialogButtonBox.AcceptRole:
                button.setStyleSheet(get_button_style(is_primary=True))
            else:
                button.setStyleSheet(get_button_style())
        
        layout.addWidget(button_box)
        
        # Show dialog
        dialog.exec()
    
    def _save_new_feature(self, dialog):
        """Save a new feature from the dialog"""
        name = self.new_feature_name.text()
        desc = self.new_feature_desc.toPlainText()
        version = self.new_feature_version.text()
        implemented = self.new_feature_implemented.isChecked()
        
        if not name or not desc or not version:
            message_box = QMessageBox()
            message_box.setStyleSheet(get_message_box_style())
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Missing Information")
            message_box.setText("Please fill in all fields.")
            message_box.exec()
            return
        
        # Add the new feature to the table
        self._add_feature(name, desc, version, implemented)
        
        # Close the dialog
        dialog.accept()
    
    def _edit_feature_dialog(self):
        """Show dialog to edit a selected feature"""
        # Get the selected row
        selected_rows = self.features_table.selectedItems()
        if not selected_rows:
            message_box = QMessageBox()
            message_box.setStyleSheet(get_message_box_style())
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("Selection Required")
            message_box.setText("Please select a feature to edit.")
            message_box.exec()
            return
        
        # Get the row of the first selected item
        row = selected_rows[0].row()
        
        # Get current values
        name = self.features_table.item(row, 0).text()
        desc = self.features_table.item(row, 1).text()
        version = self.features_table.item(row, 2).text()
        implemented = self.features_table.item(row, 3).text() == "Implemented"
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Feature")
        dialog.setStyleSheet(get_dialog_background_style())
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Create form layout
        form = QFormLayout()
        form.setSpacing(10)
        
        # Feature name field
        name_label = QLabel("Feature Name:")
        name_label.setStyleSheet(get_form_input_label_style())
        self.edit_feature_name = QLineEdit(name)
        self.edit_feature_name.setStyleSheet(get_line_edit_style())
        form.addRow(name_label, self.edit_feature_name)
        
        # Description field
        desc_label = QLabel("Description:")
        desc_label.setStyleSheet(get_form_input_label_style())
        self.edit_feature_desc = QTextEdit()
        self.edit_feature_desc.setStyleSheet(get_text_edit_style())
        self.edit_feature_desc.setPlainText(desc)
        self.edit_feature_desc.setMinimumHeight(100)
        form.addRow(desc_label, self.edit_feature_desc)
        
        # Version field
        version_label = QLabel("Version:")
        version_label.setStyleSheet(get_form_input_label_style())
        self.edit_feature_version = QLineEdit(version)
        self.edit_feature_version.setStyleSheet(get_line_edit_style())
        form.addRow(version_label, self.edit_feature_version)
        
        # Implemented status
        status_label = QLabel("Status:")
        status_label.setStyleSheet(get_form_input_label_style())
        self.edit_feature_implemented = QCheckBox("Implemented")
        self.edit_feature_implemented.setStyleSheet(get_checkbox_style())
        self.edit_feature_implemented.setChecked(implemented)
        form.addRow(status_label, self.edit_feature_implemented)
        
        layout.addLayout(form)
        
        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self._update_feature(row, dialog))
        button_box.rejected.connect(dialog.reject)
        
        # Style the buttons
        for button in button_box.buttons():
            if button_box.buttonRole(button) == QDialogButtonBox.AcceptRole:
                button.setStyleSheet(get_button_style(is_primary=True))
            else:
                button.setStyleSheet(get_button_style())
        
        layout.addWidget(button_box)
        
        # Show dialog
        dialog.exec()
    
    def _update_feature(self, row, dialog):
        """Update an existing feature"""
        name = self.edit_feature_name.text()
        desc = self.edit_feature_desc.toPlainText()
        version = self.edit_feature_version.text()
        implemented = self.edit_feature_implemented.isChecked()
        
        if not name or not desc or not version:
            message_box = QMessageBox()
            message_box.setStyleSheet(get_message_box_style())
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Missing Information")
            message_box.setText("Please fill in all fields.")
            message_box.exec()
            return
        
        # Update the feature in the table
        self.features_table.item(row, 0).setText(name)
        self.features_table.item(row, 1).setText(desc)
        self.features_table.item(row, 2).setText(version)
        
        # Update status text, background, and foreground color
        status_text = "Implemented" if implemented else "Coming Soon"
        self.features_table.item(row, 3).setText(status_text)
        self.features_table.item(row, 3).setBackground(get_status_background_color(implemented))
        self.features_table.item(row, 3).setForeground(get_status_text_color())
        
        # Close the dialog
        dialog.accept()
        
    def _delete_feature(self):
        """Delete a selected feature"""
        # Get the selected row
        selected_rows = self.features_table.selectedItems()
        if not selected_rows:
            message_box = QMessageBox()
            message_box.setStyleSheet(get_message_box_style())
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("Selection Required")
            message_box.setText("Please select a feature to delete.")
            message_box.exec()
            return
        
        # Get the row of the first selected item
        row = selected_rows[0].row()
        
        # Confirm deletion
        message_box = QMessageBox()
        message_box.setStyleSheet(get_message_box_style())
        message_box.setIcon(QMessageBox.Question)
        message_box.setWindowTitle("Confirm Deletion")
        message_box.setText(f"Are you sure you want to delete the feature '{self.features_table.item(row, 0).text()}'?")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if message_box.exec() == QMessageBox.Yes:
            # Remove the row
            self.features_table.removeRow(row)
        
    def _get_features_data(self):
        """Get all features data from the table as a list of dictionaries"""
        features_data = []
        for row in range(self.features_table.rowCount()):
            feature = {
                "name": self.features_table.item(row, 0).text(),
                "description": self.features_table.item(row, 1).text(),
                "version": self.features_table.item(row, 2).text(),
                "implemented": self.features_table.item(row, 3).text() == "Implemented"
            }
            features_data.append(feature)
        return features_data
    
    def _save_features(self):
        """Save features to a JSON file"""
        try:
            # Get data from features table
            features_data = self._get_features_data()
            
            # Get app data directory
            app_data_dir = self.settings_manager.get_app_data_dir()
            if not os.path.exists(app_data_dir):
                os.makedirs(app_data_dir)
            
            # Save data to JSON file
            features_file_path = os.path.join(app_data_dir, "features.json")
            with open(features_file_path, 'w') as f:
                json.dump(features_data, f, indent=4)
            
            # Show success message
            message_box = QMessageBox()
            message_box.setStyleSheet(get_message_box_style())
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("Features Saved")
            message_box.setText("Features have been saved successfully.")
            message_box.exec()
            
            self.logger.info(f"Features saved to {features_file_path}")
        except Exception as e:
            # Show error message
            message_box = QMessageBox()
            message_box.setStyleSheet(get_message_box_style())
            message_box.setIcon(QMessageBox.Critical)
            message_box.setWindowTitle("Error")
            message_box.setText(f"Failed to save features: {str(e)}")
            message_box.exec()
            
            self.logger.error(f"Error saving features: {str(e)}")
    
    def _load_features(self):
        """Load features from JSON file"""
        try:
            # Get app data directory
            app_data_dir = self.settings_manager.get_app_data_dir()
            features_file_path = os.path.join(app_data_dir, "features.json")
            
            # Check if file exists
            if os.path.exists(features_file_path):
                with open(features_file_path, 'r') as f:
                    features_data = json.load(f)
                
                # Clear existing features
                self.features_table.setRowCount(0)
                
                # Add loaded features
                for feature in features_data:
                    # 기존 데이터 구조 지원
                    if "release_date" in feature:
                        self._add_feature(
                            feature["name"],
                            feature["description"],
                            feature["release_date"],
                            False
                        )
                    # 새 데이터 구조 지원
                    else:
                        self._add_feature(
                            feature["name"],
                            feature["description"],
                            feature["version"],
                            feature["implemented"]
                        )
                
                self.logger.info(f"Features loaded from {features_file_path}")
            else:
                # Add default features if no saved data exists
                self._add_default_features()
                self.logger.info("No saved features found, using default features")
        except Exception as e:
            # Log error and add default features
            self.logger.error(f"Error loading features: {str(e)}")
            self._add_default_features()
    
    def _add_default_features(self):
        """Add default example features to the table"""
        # 사용자가 제공한 새 기능 목록으로 업데이트
        features_data = [
            [
                "Core Tracking & Analysis Engine",
                "Advanced tennis ball tracking with real-time analysis",
                "v1.0",
                True
            ],
            [
                "HMI & Visualization Suite",
                "Enhanced user interface with advanced visualization tools",
                "v1.5",
                False
            ],
            [
                "Temporal Event Review & Playback",
                "Instant replay functionality with frame-by-frame analysis",
                "v1.2",
                False
            ],
            [
                "Trajectory Analysis & Boundary Detection",
                "Precise serve and volley trajectory analysis with in/out detection",
                "v1.5",
                False
            ],
            [
                "Stereo Camera Calibration",
                "Advanced stereo camera system calibration tools",
                "v1.0",
                True
            ],
            [
                "3D Localization Accuracy Assessment",
                "Tools for measuring and verifying static environment 3D localization accuracy",
                "v2.0",
                False
            ],
            [
                "Real-time Event-Driven Feedback",
                "Visual feedback system with LED indicators for real-time events",
                "v1.2",
                False
            ]
        ]
        
        for feature in features_data:
            self._add_feature(feature[0], feature[1], feature[2], feature[3]) 