import QtQuick 1.0
import "../player" as Ui

Row{
    spacing: 5
    Rectangle {
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#33FFFFFF" }
            GradientStop { position: 0.3; color: "#11FFFFFF" }
        }
        border.color: "#222222"
        smooth: true
        width: 300
        height: 45
        radius: 14.0
        TextInput {
            id: search
            anchors{
                left: parent.left
                right: parent.right
                verticalCenter: parent.verticalCenter
                leftMargin: 10
            }
            text: ""
            selectByMouse: true
            cursorVisible: true
            font.pointSize: 16
            focus: true
            color: "#FFFFFF"
            Keys.onReturnPressed: {
                player.media_search(model.media, search.text) 
            }
        }
    }
    Ui.CtrlButton{
        text: "\u27A1"
        onClicked: player.media_search(model.media, search.text) 
    }
}