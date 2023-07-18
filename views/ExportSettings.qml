import QtQuick 2.0
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.3
import UM 1.1 as UM

GridLayout {
    columns: 4
    columnSpacing: 20

    Label {
        Layout.leftMargin: 20
        text: "Scale for measurements"
        color: UM.Theme.getColor("text")
        font: UM.Theme.getFont("medium")
        elide: Text.ElideRight
        renderType: Text.NativeRendering
        Layout.fillWidth: true
    }

    EnhancedTextField {
        id: scaleField
        placeholderText: "1"
        text: OnshapeService.scale
        Layout.fillWidth: true
        validator: DoubleValidator{ bottom: 0.0}
        onTextEdited: {
            OnshapeService.setScale(scaleField.text)
        }
    }

    Label {
        text: "Units"
        color: UM.Theme.getColor("text")
        font: UM.Theme.getFont("medium")
        elide: Text.ElideRight
        renderType: Text.NativeRendering
        Layout.fillWidth: true
    }

    ComboBox {
        Layout.rightMargin: 20
        id: unitsField
        Layout.fillWidth: true
        font: UM.Theme.getFont("default")
        model: ["Default", "Meter", "Centimeter", "Millimeter", "Yard", "Foot", "Inch"]
        onActivated: (index) => {
           OnshapeService.setUnits(textAt(index))
        }
    }

    Label {
        Layout.leftMargin: 20
        text: "Angle tolerance (in radians)"
        color: UM.Theme.getColor("text")
        font: UM.Theme.getFont("medium")
        elide: Text.ElideRight
        renderType: Text.NativeRendering
        Layout.fillWidth: true
    }

    EnhancedTextField {
        id: angleToleranceField
        placeholderText: ""
        Layout.fillWidth: true
        validator: DoubleValidator{ bottom: 0.0}
        onTextEdited: {
            OnshapeService.setAngle(angleToleranceField.text)
        }
    }

    Label {
        text: "Chord tolerance (in meters)"
        color: UM.Theme.getColor("text")
        font: UM.Theme.getFont("medium")
        elide: Text.ElideRight
        renderType: Text.NativeRendering
        Layout.fillWidth: true
    }

    EnhancedTextField {
        Layout.rightMargin: 20
        id: chordToleranceField
        placeholderText: ""
        Layout.fillWidth: true
        validator: DoubleValidator{ bottom: 0.0}
        onTextEdited: {
            OnshapeService.setChord(chordToleranceField.text)
        }
    }

    Label {
        Layout.bottomMargin: 20
        Layout.leftMargin: 20
        text: "Max facet width"
        color: UM.Theme.getColor("text")
        font: UM.Theme.getFont("medium")
        elide: Text.ElideRight
        renderType: Text.NativeRendering
        Layout.fillWidth: true
    }

    EnhancedTextField {
        Layout.bottomMargin: 20
        id: maxFacetWidthField
        placeholderText: ""
        Layout.fillWidth: true
        validator: DoubleValidator{ bottom: 0.0}
        onTextEdited: {
            OnshapeService.setMaxFacet(maxFacetWidthField.text)
        }
    }

    Label {
        Layout.bottomMargin: 20
        text: "Min facet width"
        color: UM.Theme.getColor("text")
        font: UM.Theme.getFont("medium")
        elide: Text.ElideRight
        renderType: Text.NativeRendering
        Layout.fillWidth: true
    }

    EnhancedTextField {
        Layout.bottomMargin: 20
        Layout.rightMargin: 20
        id: minFacetWidthField
        placeholderText: ""
        Layout.fillWidth: true
        onTextEdited: {
            OnshapeService.setMinFacet(minFacetWidthField.text)
        }
    }
}
