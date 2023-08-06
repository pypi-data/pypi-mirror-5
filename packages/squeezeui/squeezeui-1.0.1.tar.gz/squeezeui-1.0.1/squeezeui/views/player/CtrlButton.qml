import QtQuick 1.0

Rectangle {
    id: button
    gradient: Gradient {
        GradientStop { position: 0.0; color: "#33FFFFFF" }
        GradientStop { position: 0.3; color: "#11FFFFFF" }
    }
    border.color: "#222222"
    smooth: true
    width: 45
    height: 45
    radius: 14.0

    property alias text: buttontext.text

    signal clicked

    Text{
        id: buttontext
        anchors.centerIn: parent
        font.pointSize: 16
        color: "#FFFFFF"
        text: ""
    }

    MouseArea{
        id: buttonarea
        anchors.fill: parent
        hoverEnabled: true
        onEntered: parent.border.color = "#FFFFFF"
        onExited:  parent.border.color = "#222222"
        onClicked: button.clicked()
    }

    states:[
        State {
            name: "pressed"; when: buttonarea.pressed
            PropertyChanges { target: button; scale: 0.6; rotation: -45 }
        },
        State {
            name: "over"; when: buttonarea.containsMouse
            PropertyChanges { target: button; scale: 1.3; rotation: 10 }
        }
    ]
 
    Behavior on scale { SpringAnimation { spring: 2; damping: 0.1; mass: 0.3 } }
    Behavior on rotation { SpringAnimation { spring: 2; damping: 0.1; mass: 0.3 } }
    
}