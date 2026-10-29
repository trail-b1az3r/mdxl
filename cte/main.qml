import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtWebEngine

ApplicationWindow {
    id: window
    visible: true
    width: 1360
    height: 900
    minimumWidth: 860
    minimumHeight: 600
    title: "CTE — Concentrated Text Editor"
    color: "#111511"

    onClosing: function(close) {
        if (!backend.confirmCloseAll())
            close.accepted = false
    }

    palette.window: "#111511"
    palette.windowText: "#e5e9df"
    palette.text: "#e5e9df"
    palette.buttonText: "#e5e9df"
    palette.highlight: "#d5f6a0"
    palette.highlightedText: "#1d2915"

    background: Rectangle {
        color: "#111511"
        Rectangle {
            width: parent.width * 0.74
            height: parent.height * 0.68
            anchors.right: parent.right
            anchors.top: parent.top
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#202c1d" }
                GradientStop { position: 1.0; color: "#111511" }
            }
            opacity: 0.72
        }
    }

    component PillButton: Button {
        id: pill
        implicitHeight: 42
        implicitWidth: Math.max(84, contentItem.implicitWidth + 30)
        padding: 13
        font.family: backend.fontFamily
        font.pixelSize: 14
        background: Rectangle {
            radius: height / 2
            color: pill.checked ? "#d5f6a0" : (pill.hovered ? "#303a2d" : "#252d24")
            border.color: pill.checked ? "#d5f6a0" : "#3b4637"
            border.width: 1
        }
        contentItem: Text {
            text: pill.text
            color: pill.checked ? "#1d2915" : "#e5e9df"
            font: pill.font
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 82
            radius: 24
            color: "#1b201b"
            border.color: "#30382e"
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 20
                anchors.rightMargin: 16
                spacing: 14
                ColumnLayout {
                    spacing: 2
                    Text {
                        text: "CTE"
                        color: "#d5f6a0"
                        font.family: backend.fontFamily
                        font.pixelSize: 25
                        font.weight: Font.Bold
                    }
                    Text {
                        text: "Concentrated Text Editor  ·  MDXL workspace"
                        color: "#a6b29e"
                        font.family: backend.fontFamily
                        font.pixelSize: 11
                    }
                }
                Item { Layout.fillWidth: true }
                PillButton {
                    text: "Edit"
                    checkable: true
                    checked: backend.mode === "edit"
                    onClicked: backend.setMode("edit")
                }
                PillButton {
                    text: "Render"
                    checkable: true
                    checked: backend.mode === "render"
                    onClicked: backend.setMode("render")
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 68
            radius: 23
            color: "#1b201b"
            border.color: "#30382e"
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 14
                anchors.rightMargin: 14
                spacing: 9
                PillButton { text: "New page"; onClicked: backend.newDocument() }
                PillButton { text: "Open"; onClicked: backend.openDialog() }
                PillButton { text: "Save"; onClicked: backend.saveCurrent() }
                PillButton { text: "Save As"; onClicked: backend.saveAsCurrent() }
                Item { Layout.fillWidth: true }
                Text {
                    text: "Editor font"
                    color: "#c9d2c3"
                    font.family: backend.fontFamily
                    font.pixelSize: 13
                }
                ComboBox {
                    id: fontPicker
                    Layout.preferredWidth: 235
                    Layout.preferredHeight: 42
                    model: backend.fontFamilies
                    currentIndex: Math.max(0, indexOfValue(backend.fontFamily))
                    textRole: ""
                    font.family: backend.fontFamily
                    font.pixelSize: 13
                    onActivated: backend.setFontFamily(currentText)
                    contentItem: Text {
                        leftPadding: 12
                        rightPadding: fontPicker.indicator.width + 10
                        text: fontPicker.displayText
                        font: fontPicker.font
                        color: "#e5e9df"
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }
                    background: Rectangle {
                        radius: 14
                        color: "#252d24"
                        border.color: "#3b4637"
                    }
                    indicator: Text {
                        text: "▾"
                        color: "#c9d2c3"
                        font.pixelSize: 14
                        anchors.right: parent.right
                        anchors.rightMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    popup: Popup {
                        y: fontPicker.height
                        width: fontPicker.width
                        implicitHeight: Math.min(contentItem.implicitHeight, 360)
                        padding: 5
                        contentItem: ListView {
                            clip: true
                            implicitHeight: contentHeight
                            model: fontPicker.delegateModel
                            currentIndex: fontPicker.highlightedIndex
                            ScrollIndicator.vertical: ScrollIndicator {}
                        }
                        background: Rectangle {
                            color: "#20271f"
                            radius: 14
                            border.color: "#3b4637"
                        }
                    }
                    delegate: ItemDelegate {
                        width: fontPicker.width
                        text: modelData
                        font.family: modelData
                        highlighted: fontPicker.highlightedIndex === index
                        contentItem: Text {
                            text: modelData
                            font: parent.font
                            color: parent.highlighted ? "#1d2915" : "#e5e9df"
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                        }
                        background: Rectangle {
                            radius: 9
                            color: parent.highlighted ? "#d5f6a0" : "transparent"
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 24
            color: "#151915"
            border.color: "#30382e"
            clip: true
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 10

                ListView {
                    id: tabStrip
                    Layout.fillWidth: true
                    Layout.preferredHeight: 48
                    orientation: ListView.Horizontal
                    spacing: 8
                    clip: true
                    model: backend.documents
                    boundsBehavior: Flickable.StopAtBounds
                    delegate: Rectangle {
                        id: tab
                        required property int index
                        required property string title
                        required property bool modified
                        width: Math.min(285, Math.max(158, tabName.implicitWidth + 58))
                        height: 44
                        radius: 14
                        color: index === backend.currentIndex ? "#d5f6a0" : "#20251f"
                        border.color: index === backend.currentIndex ? "#d5f6a0" : "#30382e"

                        Text {
                            id: tabName
                            anchors.left: parent.left
                            anchors.leftMargin: 16
                            anchors.right: closeTab.left
                            anchors.rightMargin: 4
                            anchors.verticalCenter: parent.verticalCenter
                            text: (modified ? "• " : "") + title
                            color: index === backend.currentIndex ? "#1d2915" : "#b7c0b0"
                            font.family: backend.fontFamily
                            font.pixelSize: 13
                            font.weight: index === backend.currentIndex ? Font.DemiBold : Font.Normal
                            elide: Text.ElideRight
                        }
                        MouseArea {
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            anchors.right: closeTab.left
                            onClicked: backend.setCurrentIndex(index)
                        }
                        ToolButton {
                            id: closeTab
                            anchors.right: parent.right
                            anchors.rightMargin: 5
                            anchors.verticalCenter: parent.verticalCenter
                            width: 30
                            height: 30
                            text: "×"
                            font.pixelSize: 18
                            hoverEnabled: true
                            onClicked: backend.closeDocument(index)
                            background: Rectangle {
                                radius: 9
                                color: closeTab.hovered ? "#f2a3a0" : "transparent"
                            }
                            contentItem: Text {
                                text: closeTab.text
                                color: closeTab.hovered ? "#261a18" : (tab.index === backend.currentIndex ? "#1d2915" : "#a6b29e")
                                font: closeTab.font
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 19
                    color: "#111511"
                    clip: true

                    TextArea {
                        id: editor
                        anchors.fill: parent
                        visible: backend.mode === "edit"
                        text: backend.currentContent
                        wrapMode: TextEdit.Wrap
                        selectByMouse: true
                        persistentSelection: true
                        font.family: backend.fontFamily
                        font.pixelSize: 15
                        color: "#e5e9df"
                        selectionColor: "#48663a"
                        selectedTextColor: "#ffffff"
                        padding: 22
                        background: Rectangle { color: "#111511"; radius: 19 }
                        onTextChanged: {
                            if (text !== backend.currentContent)
                                backend.updateContent(text)
                        }
                    }

                    WebEngineView {
                        id: preview
                        anchors.fill: parent
                        visible: backend.mode === "render"
                        backgroundColor: "#111511"
                        onVisibleChanged: {
                            if (visible)
                                loadHtml(backend.renderedHtml, backend.baseUrl)
                        }
                        Connections {
                            target: backend
                            function onPreviewChanged() {
                                if (preview.visible)
                                    preview.loadHtml(backend.renderedHtml, backend.baseUrl)
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 42
            radius: 16
            color: "#1b201b"
            border.color: "#30382e"
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                Text {
                    text: backend.status
                    color: "#a6b29e"
                    font.family: backend.fontFamily
                    font.pixelSize: 12
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
                Text {
                    text: backend.wordCount + " words · " + backend.characterCount + " characters"
                    color: "#c9d2c3"
                    font.family: backend.fontFamily
                    font.pixelSize: 12
                    font.letterSpacing: 0.1
                }
            }
        }
    }
}
