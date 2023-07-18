import QtQuick 2.7
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import UM 1.1 as UM

//Item {
//    width: parent.width
//    height: dataRow.height
//    property var document: null

    RowLayout {
        id: dataRow
        spacing: 10
        width: parent.width
        property var document: null

        Image {
            Layout.preferredWidth: 70
            Layout.preferredHeight: 40
            fillMode: Image.PreserveAspectCrop
            clip: true
            source: document.thumbnailHref.href ? document.thumbnailHref.href : ""
            sourceSize.height: 40
        }

        ColumnLayout {

            Label {
                text: document.name
                color: UM.Theme.getColor("text")
                font: UM.Theme.getFont("large")
                elide: Text.ElideRight
                renderType: Text.NativeRendering
                Layout.fillWidth: true
            }

            RowLayout {
                Label {
                    text: document.modifiedByName
                    color: UM.Theme.getColor("text")
                    font: UM.Theme.getFont("small")
                    elide: Text.ElideRight
                    renderType: Text.NativeRendering
                    Layout.fillWidth: true
                }

                Label {
                    text: document.modifiedAt
                    color: UM.Theme.getColor("text")
                    font: UM.Theme.getFont("small")
                    elide: Text.ElideRight
                    renderType: Text.NativeRendering
                    Layout.fillWidth: true
                }
            }
        }

        EnhancedButton {
            text: "Show Elements"
            enabled: true

            onClicked: {
                OnshapeService.showElements(document.name, document.id, document.workspaceId)
            }
        }
    }
//}
