import QtQuick 2.2
import QtQuick.Controls 2.0
import QtQuick.Dialogs
import QtQuick.Layouts
import QtQuick.Window 2.2
import UM 1.1 as UM

// the popup window
Window {
    id: loginWindow

    // window configuration
    color: UM.Theme.getColor("viewport_background")
    minimumWidth: 400
    minimumHeight: 150
    width: minimumWidth
    height: minimumHeight
    title: "Sign in to Onshape"

    // area to provide un-focus option for input fields
    MouseArea {
        anchors.fill: parent
        focus: true
        onClicked: {
            focus = true
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20

        RowLayout {
            id: usernameRow
            width: parent.width

            Label {
                id: usernameLabel
                text: "E-Mail"
                font: UM.Theme.getFont("default")
                color: UM.Theme.getColor("text")
                renderType: Text.NativeRendering
                Layout.preferredWidth: parent.width / 2 // causes both the label and input to be the same width

                ToolTip {
                    id: usernameToolTip
                    visible: usernameLabelHoverArea.containsMouse
                    width: usernameRow.width * 0.75
                    delay: 500
                    contentItem: Label {
                        text: "Username for OnShape.com"
                        wrapMode: Text.WordWrap
                        font: UM.Theme.getFont("default")
                        renderType: Text.NativeRendering
                    }
                }

                MouseArea {
                    id: usernameLabelHoverArea
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }

            EnhancedTextField {
                id: usernameTextField
                text: OnshapeService.getUsername
                Layout.fillWidth: true
            }
        }

        RowLayout {
            id: passwordRow
            width: parent.width

            Label {
                id: passwordLabel
                text: "Password"
                font: UM.Theme.getFont("default")
                color: UM.Theme.getColor("text")
                renderType: Text.NativeRendering
                Layout.preferredWidth: parent.width / 2 // causes both the label and input to be the same width

                ToolTip {
                    id: passwordToolTip
                    visible: passwordLabelHoverArea.containsMouse
                    width: passwordRow.width * 0.75
                    delay: 500
                    contentItem: Label {
                        text: "Password for OnShape.com"
                        wrapMode: Text.WordWrap
                        font: UM.Theme.getFont("default")
                        renderType: Text.NativeRendering
                    }
                }

                MouseArea {
                    id: passwordLabelHoverArea
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }

            EnhancedTextField {
                id: passwordTextField
                text: OnshapeService.getPassword
                Layout.fillWidth: true
                echoMode: TextInput.Password
            }
        }

        RowLayout {

            Item {
                Layout.fillWidth: true
            }

            EnhancedButton {
                id: btnCancel
                text: "Cancel"
                onClicked: {
                    loginWindow.close()
                }
            }

            EnhancedButton {
                id: btnSave
                text: "Login"
                onClicked: {
                    OnshapeService.authenticate(usernameTextField.text,passwordTextField.text)
                }
            }
        }
    }
}
