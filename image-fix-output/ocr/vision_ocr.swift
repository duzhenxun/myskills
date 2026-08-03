import Foundation
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count >= 2 else {
    fputs("usage: vision_ocr.swift <image-path>\n", stderr)
    exit(1)
}

let imagePath = args[1]
let imageURL = URL(fileURLWithPath: imagePath)

guard let image = NSImage(contentsOf: imageURL) else {
    fputs("failed to load image\n", stderr)
    exit(1)
}

guard
    let tiff = image.tiffRepresentation,
    let bitmap = NSBitmapImageRep(data: tiff),
    let cgImage = bitmap.cgImage
else {
    fputs("failed to build cgimage\n", stderr)
    exit(1)
}

let request = VNRecognizeTextRequest()
request.recognitionLanguages = ["zh-Hans", "en-US"]
request.recognitionLevel = .accurate
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
do {
    try handler.perform([request])
    let observations = request.results ?? []
    for item in observations {
        guard let best = item.topCandidates(1).first else { continue }
        let box = item.boundingBox
        print("\(best.string)\t\(box.origin.x)\t\(box.origin.y)\t\(box.size.width)\t\(box.size.height)")
    }
} catch {
    fputs("ocr failed: \(error)\n", stderr)
    exit(1)
}
