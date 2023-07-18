import QtQuick 2.0
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.3
import UM 1.1 as UM

RowLayout {
    height: 40
    spacing: 0

    EnhancedTextField {
        id: searchField
        placeholderText: "Search in documents..."
        Layout.fillWidth: true
        onAccepted: {
            OnshapeService.search(searchField.text)
        }
    }

    EnhancedButton {
        text: "Search"
        onClicked: {
            OnshapeService.search(searchField.text)
        }
    }
}
