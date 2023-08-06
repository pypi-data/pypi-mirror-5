import QtQuick 1.0
import "../player" as Ui

Rectangle {
    id: popup
    opacity: 0
    color: "#88000000"
    width: parent.width / 2
    height: parent.height / 4
    anchors.centerIn: parent
    radius: 20.0
    border.color: "white"
    smooth: true

    Behavior on opacity { NumberAnimation { duration: 200 } }

    property string text: ""
    onTextChanged: {
        label.text = text
        opacity = 100
        flash.start()
    }
    Timer {
        id: flash
        interval: 2000; running: false; repeat: false
        onTriggered: {
            parent.opacity = 0
            label.text = ""
        }
    }

    Text{
        id: label
        anchors.fill: parent
        anchors.margins: 20
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font.pointSize: 20
        color: "#FFFFFF"
        text: ""
        wrapMode: Text.Wrap
    }
}