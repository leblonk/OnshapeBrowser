import QtQuick 2.7
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import UM 1.1 as UM

Item {
    width: parent.width
    height: dataRow.height
    property var element: null

    RowLayout {
        id: dataRow
        spacing: 10
        width: parent.width

        Image {
            Layout.preferredWidth: 70
            Layout.preferredHeight: 40
            fillMode: Image.PreserveAspectCrop
            clip: true
            source: element.thumbnailHref.href ? element.thumbnailHref.href : ""
            sourceSize.height: 40
        }

        Label {
            text: element.name
            color: UM.Theme.getColor("text")
            font: UM.Theme.getFont("large")
            elide: Text.ElideRight
            renderType: Text.NativeRendering
            Layout.fillWidth: true
        }

        Label {
            text: element.type
            color: UM.Theme.getColor("text")
            font: UM.Theme.getFont("large")
            elide: Text.ElideRight
            renderType: Text.NativeRendering
            Layout.fillWidth: true
        }

        EnhancedButton {
            text: "Add to build plate"
            enabled: true

            onClicked: {
                OnshapeService.addElementToBuildPlate(element.id, element.documentId, element.workspaceId, element.type, element.name)
            }
        }
    }
}
