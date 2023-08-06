import QtQuick 1.0
import "player" as Ui

Rectangle {
    width: 777; height: 555
    gradient: Gradient {
        GradientStop { position: 0.0; color: "#222222" }
        GradientStop { position: 0.1; color: "#000000" }
        GradientStop { position: 0.8; color: "#00BBBB" }
        GradientStop { position: 1.0; color: "#000000" }
    }
    Image {
            id: cover
            anchors {
                top: parent.top
                bottom: contentlist1.top
            }
            fillMode: Image.PreserveAspectFit
            smooth: true
            source: player.cover
    }

    Ui.ContentBlock{
        id: column1
        height: 135
        clip: true
        anchors {
            left: cover.right
            right: parent.right
            top: parent.top
        }
        Column {
            spacing: 0
            anchors {
                left: parent.left
                right: parent.right
                top: parent.top
                bottom: parent.bottom
                leftMargin: 10
            }
            Text {
                anchors.left: parent.left // wrapping
                anchors.right: parent.right // wrapping
                wrapMode: Text.Wrap 
                color: "white"
                font.pointSize: 22
                text: player.song
            }
            Text {
                color: "white"
                font.pointSize: 12
                text: player.album
            }
            Text {
                color: "white"
                font.pointSize: 12
                text: player.artist
            }
            Text {
                color: "white"
                font.pointSize: 12
                text: player.meta
            }
        }
    }
    Ui.ContentBlock{
        id: contentlist1
        anchors {
            left: parent.left
            right: parent.right
            top: column1.bottom
            bottom: column2.top
        }
        Ui.ContentList {
        }
    }
    Column {
        spacing: 0
        id: column2
        anchors {
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }

        Ui.ContentBlock{
            id: jumpcontrol
            Text {
                anchors{
                    top: songslider.bottom
                }
                font.pointSize: 14
                text: player.timeplayed
                color: "#FFFFFF"
            }
            Text {
                anchors{
                    top: songslider.bottom
                    right: parent.right
                }
                font.pointSize: 14
                text: player.timeleft
                color: "#FFFFFF"
            }
            Ui.Slider{
                id: songslider
                anchors.left: parent.left; anchors.right: parent.right
                radius: parent.radius
                value: player.time
                valueMin:0
                valueMax: player.duration
                Component.onCompleted: clicked.connect(player.slider_time)
            }
        }
        Ui.ContentBlock{
            id: controlpanel
            height: 70

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                spacing: 5

                Ui.CtrlButton{
                    text: ((player.power)?"On":"Off")
                    onClicked: player.button_power(!player.power)
                }
                Ui.CtrlButton{
                    text: "\u25c0\u25c0"
                    onClicked: player.button_jump_rew()
                }
                Ui.CtrlButton{
                    text: "\u25ae\u25ae"
                    onClicked: player.button_pause()
                }
                Ui.CtrlButton{
                    text: "\u25b6"
                    onClicked: player.button_play()
                }
                Ui.CtrlButton{
                    text: "\u25b6\u25b6"
                    onClicked: player.button_jump_fwd()
                }
                Ui.CtrlButton{
                    text: "\u2302\u2630"
                    onClicked: player.media_home()
                }
                Ui.CtrlButton{
                    text: "\u270E\u2637"
                    onClicked: player.media_settings()
                }
                Ui.CtrlButton{
                    text: "\u266A\u2630"
                    onClicked: player.media_playlist()
                }

                Rectangle {
                    id: volume
                    color: "#11FFFFFF"
                    border.color: "#222222"
                    smooth: true
                    radius: 14.0
                    height: 45
                    width: 250

                    MouseArea {
                        id: volumearea
                        anchors.fill: parent
                        hoverEnabled: true
                        onEntered: parent.border.color = "#FFFFFF"
                        onExited:  parent.border.color = "#222222"
                    }

                    states:[
                        State {
                            name: "over"; when: volumearea.containsMouse
                            PropertyChanges { target: volume; scale: 1.05}
                        }
                    ]

                    Behavior on scale {
                        SpringAnimation { spring: 2; damping: 0.1; mass: 0.3 }
                    }

                    Row {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.verticalCenter: parent.verticalCenter
                        Text {
                            height: 20
                            font.pointSize: 16
                            text: "\u25e2"
                            color: "#FFFFFF"
                        }

                        Ui.Slider{
                            id: volumeslider
                            width: volume.width - 50
                            value: player.volume
                            valueMin:0
                            valueMax: 100
                            Component.onCompleted:{
                                clicked.connect(player.slider_volume)
                            }
                        }
                    }
                }
            }
        }
    }
    Ui.Popup{
        text: player.popup
    }

}