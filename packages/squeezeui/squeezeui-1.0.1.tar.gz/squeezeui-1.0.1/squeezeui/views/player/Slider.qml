import QtQuick 1.0

 Rectangle {
    id: back
    width: 300; height: 20
    color: "transparent"

    property double value: 0.0
    property double valueMin: 0.0
    property double valueMax: 100.0

    function scale(coor){
        return valueMax * (coor / (container.width - 32));
    }

    onValueChanged: {
        if (!sliderarea.drag.active){
            slider.x = (value / valueMax) * (container.width - 32)
        }
    }

    signal clicked(real value)

    Rectangle {
        id: container
        width: parent.width - 4 /* initial calc needs width 
                                    because anchors is not ready */
        anchors { bottom: parent.bottom; left: parent.left
            right: parent.right; leftMargin: 2; rightMargin: 2
            bottomMargin: 2
        }
        height: 16
        radius: 8
        opacity: 0.7
        smooth: true
        gradient: Gradient {
            GradientStop { position: 0.0; color: "black" }
            GradientStop { position: 1.0; color: "white" }
        }
        MouseArea {
            id: containerarea
            anchors.fill: parent
            onClicked: back.clicked(back.scale(mouseX))
        }

        Rectangle {
             id: slider
             x: 1; y: 1; width: 30; height: 14
             radius: 6
             smooth: true
             gradient: Gradient {
                 GradientStop { position: 0.0; color: "white" }
                 GradientStop { position: 1.0; color: "black" }
             }

             MouseArea {
                id: sliderarea
                anchors.fill: parent
                drag.target: parent; drag.axis: Drag.XAxis
                drag.minimumX: 2; drag.maximumX: container.width - 32
                onReleased: back.clicked(back.scale(parent.x))
             }
        }
    }
 }