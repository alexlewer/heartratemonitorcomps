//
//  ViewController.swift
//  CameraTest
//
//  Created by Grant Terrien on 9/30/16.
//  Copyright © 2016 com.terrien. All rights reserved.
//

import UIKit
import AVFoundation

class ViewController: UIViewController, UINavigationControllerDelegate, AVCaptureVideoDataOutputSampleBufferDelegate {
    var captureDevice : AVCaptureDevice?
    var session : AVCaptureSession?
    lazy var previewLayer: AVCaptureVideoPreviewLayer = {
        let preview =  AVCaptureVideoPreviewLayer(session: self.session)
//        preview.bounds = CGRect(x: 0, y: 0, width: self.view.bounds.width, height: self.view.bounds.height)
//        preview.position = CGPoint(x: CGRectGetMidX(self.view.bounds), y: CGRectGetMidY(self.view.bounds))
        preview?.videoGravity = AVLayerVideoGravityResize
        return preview!
    }()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        captureDevice = AVCaptureDevice.defaultDevice(withMediaType: AVMediaTypeVideo) as AVCaptureDevice
        session = AVCaptureSession()
        session!.sessionPreset = AVCaptureSessionPresetHigh
        do {
            try captureDevice?.lockForConfiguration()
            captureDevice?.torchMode = .on
            captureDevice?.unlockForConfiguration()
            let deviceInput = try AVCaptureDeviceInput(device: captureDevice)
            session!.beginConfiguration()
            session!.addInput(deviceInput)
            let dataOutput = AVCaptureVideoDataOutput()
            dataOutput.videoSettings = [(kCVPixelBufferPixelFormatTypeKey as NSString) : NSNumber(value: kCVPixelFormatType_420YpCbCr8BiPlanarFullRange)]
            dataOutput.alwaysDiscardsLateVideoFrames = true
            session!.addOutput(dataOutput)
            session!.commitConfiguration()
            let queue = DispatchQueue(label: "testqueue")
            dataOutput.setSampleBufferDelegate(self, queue: queue)
            
            self.view.layer.addSublayer(previewLayer)
            previewLayer.frame = self.view.layer.frame
            session!.startRunning()
            
        } catch let error as NSError {
            NSLog("\(error)")
        }
        
        // Do any additional setup after loading the view, typically from a nib.
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    func captureOutput(_ captureOutput: AVCaptureOutput!, didOutputSampleBuffer sampleBuffer: CMSampleBuffer!, from connection: AVCaptureConnection!) {
        let buffer : CVPixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer)!
        CVPixelBufferLockBaseAddress(buffer, CVPixelBufferLockFlags(rawValue: CVOptionFlags(0)))
        
        let baseAddress = CVPixelBufferGetBaseAddressOfPlane(buffer, 0)
        let pointer = baseAddress?.assumingMemoryBound(to: UInt8.self)
        let bytesPerRow = CVPixelBufferGetBytesPerRowOfPlane(buffer, 0)
        let byteBuffer = UnsafeMutablePointer<UInt8>(pointer)!
        
        // Compute mean and standard deviation of pixel luma values
        var sum = 0
        let pixels = 1080 * bytesPerRow
        for index in 0...pixels-1 {
            sum += Int(byteBuffer[index])
        }
        let mean = (Double(sum)/Double(pixels))
        
        var sqrdDiffs = 0.0
        for index in 0...pixels-1 {
            let sqrdDiff = pow((Double(byteBuffer[index]) - mean), 2)
            sqrdDiffs += sqrdDiff
        }
        let stdDev = sqrt((Double(sqrdDiffs)/Double(pixels)))
        
        NSLog("Mean is %@", String(mean))
        NSLog("StdDev is %@", String(stdDev))
    }
}
