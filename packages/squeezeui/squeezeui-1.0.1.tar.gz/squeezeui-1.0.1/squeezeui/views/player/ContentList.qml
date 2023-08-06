import QtQuick 1.0
import "../player" as Ui

ListView {
    width: parent.width
    height: parent.height
    id: pythonList
    model: player.menuModel
    clip: true
    highlight: Rectangle {
        //visible: currentIndex>0
        color: "#44444444"
    }
    focus: true
    keyNavigationWraps: true
     
        delegate: Component {
            Rectangle {
                id: button
                width: pythonList.width
                height: 40
                clip: true
                gradient: Gradient {
                    GradientStop {
                        position: 0.0
                        color: (index % 2 == 0)?"#11FFFFFF":"#11AAAAAA"
                    }
                    GradientStop { position: 0.3; color: "#11000000" }
                }
                Image {
                    id: thumb
                    height: parent.height
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                    anchors {
                        leftMargin: 10
                        verticalCenter: parent.verticalCenter
                    }
                    source: model.media.thumb
                }
                Text {
                    id: title
                    text: model.media.name
                    color: "white"
                    font.bold: true
                    anchors {
                        leftMargin: 30
                        left: thumb.right
                    }
                    height: parent.height
                    verticalAlignment: Text.AlignVCenter
                    Behavior on font.pointSize {
                        SpringAnimation { spring: 2; damping: 0.3; mass: 0.3 }
                    }
                }
                Rectangle {
                    anchors{
                        left: thumb.right
                        leftMargin: 30
                        right: parent.right
                        top: title.bottom
                    }
                    height: parent.height
                    color: "transparent"
                    Loader {
                        id: controls
                        focus: true
                    }
                }
                Keys.onReturnPressed: player.media_selected(model.media)
                Keys.onRightPressed: player.media_selected(model.media)
                Keys.onLeftPressed: player.media_back(model.media)
                MouseArea {
                    id: buttonarea
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                    onClicked: {
                        if (mouse.button == Qt.RightButton || model.media.isSearch) {
                            if (model.media.isSearch)
                                controls.source = "ContentListSearchBox.qml"
                            else
                                controls.source = "ContentListControlButtons.qml"
                            visible = false
                            title.font.pointSize = 24
                            title.height = button.height
                            button.height += button.height
                        }
                        else
                            player.media_selected(model.media) 
                    }
                }
                states:[
                    State {
                        name: "pressed"; when: buttonarea.pressed
                        PropertyChanges { target: button; height: 60 }
                        PropertyChanges { target: title; font.pointSize: 50 }
                    },
                    State {
                        name: "over"; when: buttonarea.containsMouse
                        PropertyChanges { target: button; height: 50 }
                        PropertyChanges { target: title; font.pointSize: 18 }
                    }
                ]
                 
                    Behavior on height {SmoothedAnimation { velocity: 100 } }
            }
        }
}
