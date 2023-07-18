import QtQuick 2.7
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3

ScrollView {
    property alias model: documentsList.model
    width: parent.width
    contentWidth: width
    clip: true
    focus: true

    ListView {
        id: documentsList
        anchors.fill: parent
        width: parent.width
        delegate: Item {
            width: parent.width
            height: documentFrame.height

            Frame {
                id: documentFrame
                width: parent.width
                background: Item {}

                DocumentListItem {
                    width: parent.width
                    document: modelData
                }
            }

//            MouseArea {
//                anchors.fill: parent
//                onClicked: {
//                    documentsList.currentIndex = index;
//                    documentsList.forceActiveFocus();
//                }
//            }
        }

//        highlight: Rectangle {
//            border.color: "black"
//            color: "gray"
//            radius: 1
//            opacity: 0.1
//            focus: true
//        }
    }
}
