//
//  CameraView.swift
//  restaurant
//
//  Created by Christopher on 15/2/25.
//

import Foundation
import UIKit
import SwiftUI
import VisionKit
import Vision

struct CameraView: UIViewControllerRepresentable {
    
    var onComplete: (([UIImage]) -> Void)
    
    func makeUIViewController(context: Context) -> VNDocumentCameraViewController {
        let cameraViewController = VNDocumentCameraViewController()
        cameraViewController.delegate = context.coordinator
        
        return cameraViewController
    }
    
    func updateUIViewController(_ uiViewController: VNDocumentCameraViewController, context: Context) {
        
    }
    
    func makeCoordinator() -> Coordinator {
        return Coordinator(parent: self)
    }
    
    class Coordinator: NSObject, VNDocumentCameraViewControllerDelegate {
        
        var parent: CameraView
        init(parent: CameraView) {
            self.parent = parent
        }
        
        func documentCameraViewController(_ controller: VNDocumentCameraViewController, didFinishWith scan: VNDocumentCameraScan) {
            var numberOfPages = scan.pageCount
            let images = (0..<numberOfPages).map {
                scan.imageOfPage(at: $0)
            }
            parent.onComplete(images)
        }
    }
}
