import QtQuick 1.0
import "../player" as Ui

Row{
    spacing: 5
    Ui.CtrlButton{
        text: "\u25b6"
        onClicked: player.media_play(model.media) 
    }
    Ui.CtrlButton{
        text: "+"
        onClicked: player.media_add(model.media) 
    }
    Ui.CtrlButton{
        text: "\u27A1"
        onClicked: player.media_selected(model.media) 
    }
}