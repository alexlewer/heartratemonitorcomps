//
//  ViewController.swift
//  CameraTest
//
//  Created by Grant Terrien on 9/30/16.
//  Copyright © 2016 com.terrien. All rights reserved.
//

import UIKit
import AVFoundation
import MessageUI

public extension UIView {
    func fadeIn(withDuration duration: TimeInterval = 1.0) {
        UIView.animate(withDuration: duration, animations: {
            self.alpha = 1.0
        })
    }
}

class ViewController: UIViewController, UINavigationControllerDelegate, AVCaptureVideoDataOutputSampleBufferDelegate, MFMailComposeViewControllerDelegate {
    
    var timer = Timer()
    
    func pulse(imageView: UIImageView, interval: Double) {
        let intv = DispatchTime.now() + interval
        DispatchQueue.main.asyncAfter(deadline: intv) {
            imageView.alpha = 0.5
            imageView.fadeIn()
            self.pulse(imageView: imageView, interval: interval)
        }
    }
    
    let SCREEN_UPDATE_INTERVAL = 1.5
    
    var startTime = TimeInterval()
    
    var captureDevice : AVCaptureDevice?
    var session : AVCaptureSession?
    
    var camCovered = false
    var lapsing = false;
    
    let MAX_LUMA_MEAN = Double(100)
    let MIN_LUMA_MEAN = Double(60)
    let MAX_LUMA_STD_DEV = Double(20)
    
    var brightnesses : [Double]?
    
    var stateQueue : YChannelStateQueue?
    var heartRates : [Int]?
    var brightnessDerivatives : [Int]?
    
    var obsTime : [Double]?
    var beginningTime : Double?
    var stateCount : Int?
    var bpmRecords : [Int]?
    var HRCount : Int?
    var isFirstHR:Bool?
    var lastCalculated : Date?
    
    var previousBPM: Int?
    var previousBrightnessDifference : Double?
    
    var previousCover : Bool?
    var camCoverStartTime : Double?
    var camCoverStartIndex : Int?
    var needToFindNextPeak : Bool?
    var nextPeakIndex : Int?
    var tempObservation : [Int]?
    var tempObsTime : [Double]?
    var tempBrightness : [Double]?
    var previousMaxBrightness : Double?
    
    var currentBPM : Int?
    var uiTimer : Timer?
    
    var previousMeasuredBPM : Int?
    
    func initialize() {
        stateQueue = YChannelStateQueue()
        heartRates = [Int]()
        brightnessDerivatives = [Int]()
        brightnesses = [Double]()
        obsTime = [Double]()
        previousBrightnessDifference = -1
        bpmRecords = [0,0,0,0,0,0]
        HRCount = 0
        isFirstHR = true
        previousBPM = 0
        previousCover = false
        camCoverStartTime = 0.0
        nextPeakIndex = 0
        tempObservation = []
        tempObsTime = []
        tempBrightness = []
        previousMaxBrightness = -1.0
        currentBPM = 0
        previousMeasuredBPM = 0
    }
    
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
    @IBOutlet var BPMText: UILabel!
    
    @IBAction func goInfo(_ sender: Any) {
        if button.currentTitle == "STOP" {
            session!.stopRunning()
            toggleFlashlight()
        }
    }
    
    func updateDisplayedBPM() {
        if self.currentBPM! != 0 {
            DispatchQueue.main.async {
                self.BPMText.text = String(self.currentBPM!) + " BPM"
                if self.currentBPM! > 100 {
                    self.BPMText.frame.size.width = 190
                    self.heartView.removeFromSuperview()
                    self.displayHeart(imageName: "Heart_normal")
                    self.pulse(imageView: self.heartView, interval: 0.5)
                }
                else {
                    self.BPMText.frame.size.width = 160
                    self.heartView.removeFromSuperview()
                    self.displayHeart(imageName: "Heart_normal")
                    self.pulse(imageView: self.heartView, interval: 1)
                }
            }
        }
    }
    
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
            uiTimer = Timer.scheduledTimer(timeInterval: SCREEN_UPDATE_INTERVAL, target: self, selector: #selector(ViewController.updateDisplayedBPM), userInfo: nil, repeats: true)
        }
        else {
            heartView.removeFromSuperview()
            displayHeart(imageName: "Heart_inactive")
            uiTimer?.invalidate()
            // End camera processes
            session!.stopRunning()
            toggleFlashlight()
            
            timer.invalidate()
            button.setBackgroundImage(UIImage(named: "Button_start"), for: UIControlState.normal)
            button.setTitle("START", for: UIControlState.normal)
            hint1.text = "Ready to start."
            hint2.text = "Please hit the START button."
            timerText.text = "00:00:00"
            BPMText.frame.size.width = 175
            BPMText.text = "- - - BPM"
        }
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        displayHeart(imageName: "Heart_inactive")
        initialize()
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
        }
        else {
            initialize()
            timer.invalidate()
            heartView.removeFromSuperview()
            displayHeart(imageName: "Heart_normal")
            hint1.text = "Waiting for signal."
            hint2.text = "Please cover the camera with your finger."
            timerText.text = "00:00:00"
            BPMText.frame.size.width = 175
            BPMText.text = "- - - BPM"
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
        
        let mean = detectFingerCoverage(bytesPerRow: bytesPerRow, byteBuffer: byteBuffer)
        
        if self.camCovered {
            useCaptureOutputForHeartRateEstimation(mean: mean, bytesPerRow: bytesPerRow)
        }
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
            let sqrdDiff = (Double(byteBuffer[index]) - mean) * (Double(byteBuffer[index]) - mean)
            sqrdDiffs += sqrdDiff
        }
        let stdDev = sqrt((Double(sqrdDiffs)/Double(pixels)))
        
        return (mean, stdDev);
    }
    
    func detectFingerCoverage(bytesPerRow: Int, byteBuffer: UnsafeMutablePointer<UInt8>) -> Double {
        
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
                        if !self.camCovered && self.button.currentTitle == "STOP" {
                            self.updateDisplay()
                        }
                        self.lapsing = false;
                    })
                } else if !self.lapsing && self.button.currentTitle == "STOP" {
                    self.updateDisplay()
                }
            }
        }
        return mean
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
    
    
    //****************** Viterbi and heart rate estimation *********************
    
    func viterbi(obs:Array<Int>, trans:Array<Array<Double>>, emit:Array<Array<Double>>, states: Array<Int>, initial:Array<Double>)->(Double, [Int]){
        var vit = [[Int:Double]()]
        var path = [Int:[Int]]()
        
        for s in states{
            vit[0][s] = initial[s] * emit[s][obs[0]]
            path[s] = [s]
        }
        for i in 1..<obs.count{
            vit.append([:])
            var newPath = [Int:[Int]]()
            
            for state1 in states{
                var transMax = DBL_MIN
                var maxProb = DBL_MIN
                var bestState:Int?
    
                for state2 in states{
                    let transProb = vit[i-1][state2]! * trans[state2][state1]
                    if transProb > transMax{
                        transMax = transProb
                        maxProb = transMax * emit[state1][obs[i]]
                        vit[i][state1] = maxProb
                        bestState = state2
                        newPath[state1] = path[bestState!]! + [state1]
                    }
                }
                
            }
            path = newPath
        }
        let len = obs.count - 1
        var bestState:Int?
        var maxProb = DBL_MIN
        for state in states{
            if vit[len][state]! > maxProb{
                maxProb = vit[len][state]!
                bestState = state
            }
        }
        return (maxProb, path[bestState!]!)
        
    }
  
    func calculate(states:Array<Int>, brightnesses: [Double]){
        var previous = (states[0], brightnesses[0])
        var validBPM = 0
        var tempBPM = 0
        var interval = 0.0
        var brightnessDifference = Double(-1)
        
        for i in 0..<states.count{
            if states[i] == 3 && previous.0 == 2 {
                brightnessDifference = abs(previous.1-brightnesses[i])
                if previousBrightnessDifference == -1 {
                    previousBrightnessDifference = brightnessDifference
                }
            }
            if (states[i]==0 && previous.0 == 3) {
                if beginningTime != nil {
                    interval = (obsTime?[i])! - beginningTime!
                    validBPM = Int(60 / interval)
                    bpmRecords?[HRCount! % 6] = validBPM
                    if HRCount! >= 6{
                        tempBPM = (validBPM + previousBPM!)/2
                        var avg:Double = 0
                        var sum:Double = 0
                        var tempRecords = bpmRecords?.sorted()
                        for k in 1..<5{
                            sum = sum + Double((tempRecords?[k])!)
                        }
                        avg = sum/4
                        var usefulEnds:Int = 0
                        if abs(Double((tempRecords?[0])!) - avg)<=10{
                            sum = sum + Double((tempRecords?[0])!)
                            usefulEnds += 1
                        }
                        if abs(Double((tempRecords?[5])!) - avg)<=10{
                            sum = sum + Double((tempRecords?[5])!)
                            usefulEnds += 1
                        }
                        avg = sum / Double(4 + usefulEnds)
                        if (abs(tempBPM - Int(avg)) <= 10)
                            && (tempBPM >= 30) && (tempBPM <= 300) {
                            previousBPM = tempBPM
                            validBPM = ((tempRecords?[2])!+(tempRecords?[3])!+tempBPM) / 3
                        } else {
                            validBPM = Int(avg)
                        }
                        self.currentBPM = validBPM
                    } else{
                        previousBPM = validBPM
                    }
                    HRCount = HRCount! + 1
                }
    
                beginningTime = obsTime?[i]
                
            }
            
            previous = (states[i], brightnesses[i])
            previousBrightnessDifference = brightnessDifference
        }

    }

    
    func useCaptureOutputForHeartRateEstimation(mean: Double, bytesPerRow: Int) {
        let currentTime = NSDate().timeIntervalSince1970
        let trans = [[0.6794, 0.3206, 0.0, 0.0],
                     [0.0, 0.5366, 0.4634, 0.0],
                     [0.0, 0.0, 0.3485, 0.6516],
                     [0.1508, 0.0, 0.0, 0.8492]]
        
        let emit = [[0.6884, 0.0015, 0.3002, 0.0099],
                    [0.0, 0.7205, 0.0102, 0.2694],
                    [0.2894, 0.3731, 0.3362, 0.0023],
                    [0.0005, 0.8440, 0.0021, 0.1534]]
        let p = [0.25, 0.20, 0.10, 0.45]
        let states = [0,1,2,3]
        
        if (self.camCovered) {
            let pixels = 1080 * bytesPerRow
            let value = mean/Double(pixels)
            stateQueue?.addValue(value: value)
            if (self.tempObservation?.count != 0){
                if (((tempObsTime?.last!)! - (tempObsTime?.first!)!) >= 2.0) {
                    for i in 0..<self.tempObservation!.count {
                        if (((tempObsTime?.last!)! - (tempObsTime?[self.tempObsTime!.count - i - 1])!) >= 1.0) {
                            self.brightnessDerivatives? = self.brightnessDerivatives! + tempObservation!
                            self.obsTime? = self.obsTime! + tempObsTime!
                            self.brightnesses? = self.brightnesses! + tempBrightness!
                        } else {
                            self.tempBrightness?.removeLast(i)
                            self.tempObsTime?.removeLast(i)
                            self.tempObservation?.removeLast(i)
                        }
                    }
                }
                tempObsTime = []
                tempObservation = []
                tempBrightness = []
            }
            self.camCoverStartTime = currentTime
            self.needToFindNextPeak = true
            if (self.brightnessDerivatives?.count != 0){
                if (((self.obsTime?.last)! - (self.obsTime?.first)!) >= 3.0){
                    self.calculate(states: self.viterbi(obs:self.brightnessDerivatives!, trans:trans, emit:emit, states:states, initial:p).1, brightnesses: brightnesses!)
                }
            }
            
            self.tempObservation!.append((stateQueue?.getState())!.0)
            self.tempBrightness!.append((stateQueue?.getState())!.1)
            self.tempObsTime!.append(currentTime)
            if (needToFindNextPeak!) {
                if ((currentTime - self.camCoverStartTime!) >= 1.0) {
                    self.needToFindNextPeak = false
                } else {
                    if (self.previousMaxBrightness! < (tempBrightness?.last!)!) {
                        self.previousMaxBrightness! = (tempBrightness?.last!)!
                        tempObsTime = [(tempObsTime?.last!)!]
                        tempObservation = [(tempObservation?.last!)!]
                        tempBrightness = [(tempBrightness?.last!)!]
                    }
                }
                
            }
            
            if (stateQueue?.getState().0 != -1) {
                obsTime!.append(NSDate().timeIntervalSince1970)
                brightnesses!.append((stateQueue?.getState().1)!)
                brightnessDerivatives!.append((stateQueue?.getState())!.0)
            }
            
        }
    }
}
