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
    
    @IBAction func openCamera(_ sender: AnyObject) {
        let session = AVCaptureSession()
        session.sessionPreset = AVCaptureSessionPresetHigh
        do {
              let deviceInput = try AVCaptureDeviceInput(device: captureDevice)
        session.beginConfiguration()
        session.addInput(deviceInput)
        let dataOutput = AVCaptureVideoDataOutput()
            dataOutput.videoSettings = [(kCVPixelBufferPixelFormatTypeKey as NSString) : NSNumber(value: kCVPixelFormatType_420YpCbCr8BiPlanarFullRange)]
        dataOutput.alwaysDiscardsLateVideoFrames = true
        session.addOutput(dataOutput)
        session.commitConfiguration()
        let queue = DispatchQueue(label: "testqueue")
        dataOutput.setSampleBufferDelegate(self, queue: queue)
        session.startRunning()
        }
        catch let error as NSError {
            NSLog("\(error)")
        }
        }

    override func viewDidLoad() {
        super.viewDidLoad()
        captureDevice = AVCaptureDevice.defaultDevice(withMediaType: AVMediaTypeVideo) as AVCaptureDevice
        do {
            try captureDevice?.lockForConfiguration()
            captureDevice?.torchMode = .on
            captureDevice?.unlockForConfiguration()
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
        let buffer = CMSampleBufferGetImageBuffer(sampleBuffer)!
        CVPixelBufferLockBaseAddress(buffer, CVPixelBufferLockFlags(rawValue: CVOptionFlags(0)))
        let baseAddress = CVPixelBufferGetBaseAddressOfPlane(buffer, 0)
        let ui8 = baseAddress?.load(as: UInt8.self)
        print(ui8)
        let newPointer = baseAddress?.advanced(by: 1)
        let ui82 = newPointer?.load(as: UInt8.self)
        print(ui82)
        
        
        }
}

