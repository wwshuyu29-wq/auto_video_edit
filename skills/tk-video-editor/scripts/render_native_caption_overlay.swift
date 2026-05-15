import AppKit
import Foundation

struct CaptionStyle: Decodable {
    var lines: [String]?
    var font_size: Double?
    var line_gap: Double?
    var y_ratio: Double?
    var max_width: Double?
    var highlight_terms: [String]?
    var highlight_fill: [Int]?
}

struct CaptionSpec: Decodable {
    var text: String
    var beat: String
    var priority: String
    var width: Int
    var height: Int
    var output: String
    var style: CaptionStyle?
}

func color(_ rgba: [Int]?, fallback: NSColor) -> NSColor {
    guard let rgba = rgba, rgba.count >= 3 else { return fallback }
    let a = rgba.count >= 4 ? CGFloat(rgba[3]) / 255.0 : 1.0
    return NSColor(
        calibratedRed: CGFloat(rgba[0]) / 255.0,
        green: CGFloat(rgba[1]) / 255.0,
        blue: CGFloat(rgba[2]) / 255.0,
        alpha: a
    )
}

func wordKey(_ word: String) -> String {
    let allowed = CharacterSet.alphanumerics.union(CharacterSet(charactersIn: "/.-"))
    return word.trimmingCharacters(in: allowed.inverted).lowercased()
}

func attributed(_ text: String, font: NSFont, fill: NSColor, paragraph: NSParagraphStyle) -> NSAttributedString {
    NSAttributedString(string: text, attributes: [
        .font: font,
        .foregroundColor: fill,
        .paragraphStyle: paragraph
    ])
}

func textSize(_ text: String, font: NSFont) -> NSSize {
    let attrs: [NSAttributedString.Key: Any] = [.font: font]
    return (text as NSString).size(withAttributes: attrs)
}

func wrapText(_ text: String, font: NSFont, maxWidth: CGFloat) -> [String] {
    let words = text.split(separator: " ").map(String.init)
    guard var current = words.first else { return [] }
    var lines: [String] = []
    for word in words.dropFirst() {
        let candidate = "\(current) \(word)"
        if textSize(candidate, font: font).width <= maxWidth {
            current = candidate
        } else {
            lines.append(current)
            current = word
        }
    }
    lines.append(current)
    return lines
}

func drawOutlinedLine(
    drawText: String,
    in rect: NSRect,
    font: NSFont,
    paragraph: NSParagraphStyle,
    fill: NSColor,
    highlightTerms: Set<String>,
    highlightFill: NSColor
) {
    let words = drawText.split(separator: " ").map(String.init)
    guard !words.isEmpty else { return }
    let spaceW = textSize(" ", font: font).width
    let widths = words.map { textSize($0, font: font).width }
    let totalW = widths.reduce(0, +) + spaceW * CGFloat(max(0, words.count - 1))
    var x = rect.midX - totalW / 2.0
    let y = rect.minY

    for (idx, word) in words.enumerated() {
        let key = wordKey(word)
        let isHighlighted = highlightTerms.contains(key) || highlightTerms.contains { term in
            term.count > 3 && key.contains(term)
        }
        let fg = isHighlighted ? highlightFill : fill
        let wordRect = NSRect(x: x, y: y, width: widths[idx] + 4, height: rect.height)
        let outline = attributed(word, font: font, fill: .black, paragraph: paragraph)
        let main = attributed(word, font: font, fill: fg, paragraph: paragraph)
        let offsets: [(CGFloat, CGFloat)] = [
            (-5, 0), (5, 0), (0, -5), (0, 5),
            (-4, -4), (-4, 4), (4, -4), (4, 4),
            (-2, 0), (2, 0), (0, -2), (0, 2)
        ]
        for (dx, dy) in offsets {
            outline.draw(with: wordRect.offsetBy(dx: dx, dy: dy), options: [.usesLineFragmentOrigin, .usesFontLeading])
        }
        main.draw(with: wordRect, options: [.usesLineFragmentOrigin, .usesFontLeading])
        x += widths[idx] + spaceW
    }
}

let specURL = URL(fileURLWithPath: CommandLine.arguments[1])
let data = try Data(contentsOf: specURL)
let spec = try JSONDecoder().decode(CaptionSpec.self, from: data)
let style = spec.style

let W = spec.width
let H = spec.height
guard let rep = NSBitmapImageRep(
    bitmapDataPlanes: nil,
    pixelsWide: W,
    pixelsHigh: H,
    bitsPerSample: 8,
    samplesPerPixel: 4,
    hasAlpha: true,
    isPlanar: false,
    colorSpaceName: .deviceRGB,
    bitmapFormat: [.alphaFirst],
    bytesPerRow: 0,
    bitsPerPixel: 0
) else {
    fatalError("Could not create bitmap context")
}

NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
NSColor.clear.setFill()
NSRect(x: 0, y: 0, width: W, height: H).fill()

let fontSize = CGFloat(style?.font_size ?? (spec.priority == "large" ? 66 : 70))
let lineGap = CGFloat(style?.line_gap ?? 8)
let maxWidth = CGFloat(style?.max_width ?? 900)
let paragraph = NSMutableParagraphStyle()
paragraph.alignment = .center
paragraph.lineSpacing = lineGap

let font = NSFont.systemFont(ofSize: fontSize, weight: .heavy)
let lines = style?.lines ?? (spec.text.contains("\n") ? spec.text.components(separatedBy: "\n").filter { !$0.isEmpty } : wrapText(spec.text, font: font, maxWidth: maxWidth))
let lineHeight = fontSize + lineGap
let blockH = CGFloat(lines.count) * lineHeight
let yRatio = CGFloat(style?.y_ratio ?? (spec.beat == "hook" ? 0.40 : 0.43))

// Convert top-origin video coordinates into AppKit's bottom-origin drawing space.
let topY = CGFloat(H) * yRatio - blockH / 2.0
let highlightTerms = Set((style?.highlight_terms ?? []).map { $0.lowercased() })
let highlightFill = color(style?.highlight_fill, fallback: NSColor(calibratedRed: 1.0, green: 0.92, blue: 0.44, alpha: 1.0))

for (index, line) in lines.enumerated() {
    let topLineY = topY + CGFloat(index) * lineHeight
    let appKitY = CGFloat(H) - topLineY - lineHeight
    let rect = NSRect(x: (CGFloat(W) - maxWidth) / 2.0, y: appKitY, width: maxWidth, height: lineHeight + 16)
    drawOutlinedLine(
        drawText: line,
        in: rect,
        font: font,
        paragraph: paragraph,
        fill: .white,
        highlightTerms: highlightTerms,
        highlightFill: highlightFill
    )
}

NSGraphicsContext.restoreGraphicsState()

guard let png = rep.representation(using: .png, properties: [:]) else {
    fatalError("Could not render PNG")
}

try png.write(to: URL(fileURLWithPath: spec.output))
