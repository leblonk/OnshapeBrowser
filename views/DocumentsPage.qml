import QtQuick 2.2
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import UM 1.1 as UM

ColumnLayout {
    id: detailsPage
    property var documents
    property var elements

    EnhancedButton {
        text: "Back to documents"
        visible: OnshapeService.elementsVisible
        Layout.leftMargin: 20
        Layout.topMargin: 10
        Layout.bottomMargin: 10
        onClicked: {
            OnshapeService.hideElements()
        }
    }

    DocumentsList {
        id: documentsList
        model: documents
        visible: OnshapeService.documentsVisible
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.leftMargin: 20
        Layout.rightMargin: 20
        Layout.bottomMargin: 20
    }

    Label {
        id: documentsListEmpty
        text: "No documents found."
        visible: documents.length == 0 && OnshapeService.documentsVisible
        font: UM.Theme.getFont("medium")
        color: UM.Theme.getColor("text_inactive")
        renderType: Text.NativeRendering
        wrapMode: Label.WordWrap
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.leftMargin: 20
    }

    Label {
        id: currentDocumentName
        text: OnshapeService.currentDocumentName
        color: UM.Theme.getColor("text")
        font: UM.Theme.getFont("large")
        elide: Text.ElideRight
        renderType: Text.NativeRendering
        width: parent.width
        visible: OnshapeService.elementsVisible
        Layout.leftMargin: 20
        Layout.rightMargin: 20
    }

    ElementsList {
        id: elementsList
        model: elements
        visible: OnshapeService.elementsVisible
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.leftMargin: 20
        Layout.rightMargin: 20
        Layout.bottomMargin: 20
    }

    Label {
        id: elementsListEmpty
        text: "No elements found."
        visible: elements.length == 0 && OnshapeService.elementsVisible
        font: UM.Theme.getFont("medium")
        color: UM.Theme.getColor("text_inactive")
        renderType: Text.NativeRendering
        wrapMode: Label.WordWrap
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.leftMargin: 20
    }
}
