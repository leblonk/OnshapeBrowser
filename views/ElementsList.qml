import QtQuick 2.7
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3

ScrollView {
    property alias model: elementsList.model
    width: parent.width
    contentWidth: width
    clip: true

    ListView {
        id: elementsList
        width: parent.width
        spacing: 20
        delegate: Item {
            width: parent.width
            height: childrenRect.height

            ElementListItem {
                width: parent.width
                element: modelData
            }
        }
    }
}
