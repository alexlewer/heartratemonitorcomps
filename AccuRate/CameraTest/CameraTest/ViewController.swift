//
//  ViewController.swift
//  CameraTest
//
//  Created by Grant Terrien on 9/30/16.
//  Copyright © 2016 com.terrien. All rights reserved.
//

import UIKit
import AVFoundation

public extension UIView {
    func fadeIn(withDuration duration: TimeInterval = 1.0) {
        UIView.animate(withDuration: duration, animations: {
            self.alpha = 1.0
        })
    }
}

class ViewController: UIViewController, UINavigationControllerDelegate, AVCaptureVideoDataOutputSampleBufferDelegate {
    
    var timer = Timer()
    
    func pulse(imageView: UIImageView, interval: Double) {
        let intv = DispatchTime.now() + interval
        DispatchQueue.main.asyncAfter(deadline: intv) {
            imageView.alpha = 0.5
            imageView.fadeIn()
            self.pulse(imageView: imageView, interval: interval)
        }
    }
    
    var startTime = TimeInterval()
    
    var captureDevice : AVCaptureDevice?
    var session : AVCaptureSession?
    
    var camCovered = false
    var lapsing = false;
    
    let MAX_LUMA_MEAN = Double(100)
    let MIN_LUMA_MEAN = Double(60)
    let MAX_LUMA_STD_DEV = Double(20)
    
    func displayHeart(imageName: String) {
        heartView = UIImageView(frame: CGRect(x: 0, y: 0, width: 170, height: 170))
        self.view.addSubview(heartView)
        heartView.translatesAutoresizingMaskIntoConstraints = false
        heartView.centerXAnchor.constraint(equalTo: view.centerXAnchor).isActive = true
        heartView.centerYAnchor.constraint(equalTo: view.centerYAnchor).isActive = true
        heartView.image = UIImage(named: imageName)
    }
    
    @IBOutlet var timerText: UILabel!
    @IBOutlet var button: UIButton!
    @IBOutlet var hint1: UILabel!
    @IBOutlet var hint2: UILabel!
    @IBOutlet var heartView: UIImageView!
    
    @IBAction func start(sender: AnyObject) {
        if button.currentTitle == "START" {
            heartView.image = UIImage(named: "Heart_normal")
            heartView.alpha = 0.25
            heartView.fadeIn()
            button.setBackgroundImage(UIImage(named: "Button_stop"), for: UIControlState.normal)
            button.setTitle("STOP", for: UIControlState.normal)
            hint1.text = "Waiting for signal."
            hint2.text = "Please cover the camera with your finger."
            startCameraProcesses()
        }
        else {
            // End camera processes
            session!.stopRunning()
            toggleFlashlight()
            
            timer.invalidate()
            heartView.removeFromSuperview()
            displayHeart(imageName: "Heart_inactive")
            button.setBackgroundImage(UIImage(named: "Button_start"), for: UIControlState.normal)
            button.setTitle("START", for: UIControlState.normal)
            hint1.text = "Ready to start."
            hint2.text = "Please hit the START button."
            timerText.text = "00:00:00"
        }
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        displayHeart(imageName: "Heart_inactive")
        // Do any additional setup after loading the view, typically from a nib.
    }
    
    func toggleFlashlight() {
        captureDevice = AVCaptureDevice.defaultDevice(withMediaType: AVMediaTypeVideo) as AVCaptureDevice
        do {
            try captureDevice?.lockForConfiguration()
            if captureDevice?.torchMode == .on {
                captureDevice?.torchMode = .off
            } else {
                captureDevice?.torchMode = .on
            }
        } catch let error as NSError {
            NSLog("\(error)")
        }
    }
    
    
    func startCameraProcesses() {
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
            let queue = DispatchQueue(label: "queue")
            dataOutput.setSampleBufferDelegate(self, queue: queue)
            session!.startRunning()
            
        } catch let error as NSError {
            NSLog("\(error)")
        }
        
    }
    
    func updateDisplay() {
        if self.camCovered {
            hint1.text = "Signal detected!"
            hint2.text = "Please do not remove your finger from the camera."
            let aSelector : Selector = #selector(ViewController.updateTime)
            timer = Timer.scheduledTimer(timeInterval: 0.01, target: self, selector: aSelector, userInfo: nil, repeats: true)
            startTime = NSDate.timeIntervalSinceReferenceDate
            pulse(imageView: self.heartView, interval: 1.5)
        }
        else {
            timer.invalidate()
            heartView.removeFromSuperview()
            displayHeart(imageName: "Heart_normal")
            hint1.text = "Waiting for signal."
            hint2.text = "Please cover the camera with your finger."
            timerText.text = "00:00:00"
        }
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    func getCoverageFromBrightness(lumaMean: Double, lumaStdDev: Double) -> Bool{
        if ((lumaMean < MAX_LUMA_MEAN) && (lumaMean > MIN_LUMA_MEAN) && (lumaStdDev < MAX_LUMA_STD_DEV)) {
            return true
        }
        return false
    }
    
    func captureOutput(_ captureOutput: AVCaptureOutput!, didOutputSampleBuffer sampleBuffer: CMSampleBuffer!, from connection: AVCaptureConnection!) {
        let buffer : CVPixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer)!
        CVPixelBufferLockBaseAddress(buffer, CVPixelBufferLockFlags(rawValue: CVOptionFlags(0)))
        
        let baseAddress = CVPixelBufferGetBaseAddressOfPlane(buffer, 0)
        let pointer = baseAddress?.assumingMemoryBound(to: UInt8.self)
        let bytesPerRow = CVPixelBufferGetBytesPerRowOfPlane(buffer, 0)
        let byteBuffer = UnsafeMutablePointer<UInt8>(pointer)!
        
        detectFingerCoverage(bytesPerRow: bytesPerRow, byteBuffer: byteBuffer)
        
        // Compute mean and standard deviation of pixel luma values
        
    }
    
    func getMeanAndStdDev(bytesPerRow: Int, byteBuffer: UnsafeMutablePointer<UInt8>) -> (Double, Double){
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
        
        return (mean, stdDev);
    }
    
    func detectFingerCoverage(bytesPerRow: Int, byteBuffer: UnsafeMutablePointer<UInt8>) {
        
        let meanAndStdDev = getMeanAndStdDev(bytesPerRow: bytesPerRow, byteBuffer: byteBuffer)
        
        let mean = meanAndStdDev.0
        let stdDev = meanAndStdDev.1
        
        let covered = getCoverageFromBrightness(lumaMean: mean, lumaStdDev: stdDev)
        
        DispatchQueue.main.async {
            if covered != self.camCovered {
                self.camCovered = covered
                if !self.camCovered && !self.lapsing {
                    self.lapsing = true;
                    DispatchQueue.main.asyncAfter(deadline: .now() + .seconds(1), execute: {
                        if !self.camCovered {
                            self.updateDisplay()
                        }
                        self.lapsing = false;
                    })
                } else if !self.lapsing {
                    self.updateDisplay()
                }
            }
        }
    }
    
    func updateTime() {
        let currentTime = NSDate.timeIntervalSinceReferenceDate
        //Find the difference between current time and start time.
        var elapsedTime: TimeInterval = currentTime - startTime
        //Calculate the minutes in elapsed time.
        let minutes = UInt8(elapsedTime / 60.0)
        elapsedTime -= (TimeInterval(minutes) * 60)
        //Calculate the seconds in elapsed time.
        let seconds = UInt8(elapsedTime)
        elapsedTime -= TimeInterval(seconds)
        //Find out the fraction of milliseconds to be displayed.
        let fraction = UInt8(elapsedTime * 100)
        //Add the leading zero for minutes, seconds and millseconds and store them as string constants
        let strMinutes = String(format: "%02d", minutes)
        let strSeconds = String(format: "%02d", seconds)
        let strFraction = String(format: "%02d", fraction)
        //Concatenate minuets, seconds and milliseconds as assign it to the UILabel
        timerText.text = "\(strMinutes):\(strSeconds):\(strFraction)"
    }
    
}
