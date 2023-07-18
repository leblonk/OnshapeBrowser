import QtQuick 2.2
import QtQuick.Controls 2.0
import QtQuick.Dialogs
import QtQuick.Layouts
import QtQuick.Window 2.2
import UM 1.1 as UM

// the popup window
Window {
    id: mainWindow

    // window configuration
    color: UM.Theme.getColor("viewport_background")
    minimumWidth: Math.round(UM.Theme.getSize("modal_window_minimum").width)
    minimumHeight: Math.round(UM.Theme.getSize("modal_window_minimum").height)
    width: minimumWidth
    height: minimumHeight
    title: "Onshape Browser"

    // area to provide un-focus option for search field
    MouseArea {
        anchors.fill: parent
        focus: true
        onClicked: {
            focus = true
        }
    }

    Page {
    	width: parent.width
        height: parent.height
        anchors.fill: parent

        // the header
        header: RowLayout {
//            Layout.alignment: Qt.AlignTop
            visible: !OnshapeService.elementsVisible
            width: parent.width
            height: 40
            spacing: 10

            Searchbar {
                id: searchbar
                Layout.fillWidth: true
            }

            EnhancedButton {
                id: loginButton
                text: "Login"
                onClicked: {
                    OnshapeService.openLoginWindow()
                }
            }
        }

        DocumentsPage {
            anchors.fill: parent
//            width: parent.width
//            Layout.fillHeight: true
            documents: OnshapeService.documents
            elements: OnshapeService.elements
            visible: true
        }

        footer: ExportSettings {
            width: parent.width
            visible: OnshapeService.elementsVisible
        }
    }
}
