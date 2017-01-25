//
//  ViewController.swift
//  AccuRate
//
//  Contains most logic for both controlling the view, and calculating the heart rate.
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
    
    var startTime = TimeInterval()
    
    var captureDevice : AVCaptureDevice?
    var session : AVCaptureSession?
    
    var camCovered = false
    var lapsing = false;
    
    let MAX_LUMA_MEAN = Double(100)
    let MIN_LUMA_MEAN = Double(60)
    let MAX_LUMA_STD_DEV = Double(20)
    
    var stateQueue : YChannelStateQueue?
    var heartRates : [Int]?
    var observation : [Int]?
    
    var obsTime : [Double]?
    var beginningTime : Double?
    var stateCount : Int?
    
    var lastCalculated : Date?
    
    var previousBPM: Int?
    var validBPM: Int?
    
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
            initializeRateCalculationVars()
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
        }
        else {
            heartView.removeFromSuperview()
            displayHeart(imageName: "Heart_inactive")
            
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
        initializeRateCalculationVars()
    }
    
    func initializeRateCalculationVars() {
        stateQueue = YChannelStateQueue()
        heartRates = [Int]()
        observation = [Int]()
        obsTime = [Double]()
        previousBPM = 0
        validBPM = 0
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
        
        let meanAndStdDev = getMeanAndStdDev(bytesPerRow: bytesPerRow, byteBuffer: byteBuffer)
        
        detectFingerCoverage(bytesPerRow: bytesPerRow, byteBuffer: byteBuffer, meanAndStdDev: meanAndStdDev)
        
        if self.camCovered {
            useCaptureOutputForHeartRateEstimation(mean: meanAndStdDev.0, bytesPerRow: bytesPerRow)
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
    
    func detectFingerCoverage(bytesPerRow: Int, byteBuffer: UnsafeMutablePointer<UInt8>, meanAndStdDev: (Double, Double)) {
        
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
    
    func calculate(states:Array<Int>, since: Double){
        var previous = states[0]
        var measuredBPM = 0
        for i in 0..<states.count{
            if (states[i]==0 && previous == 3) {
                // We want to display data points only if two of them in a row are consistent.
                if beginningTime != nil {
                    let interval = (obsTime?[i])! - beginningTime!
                    print("interval", interval)
                    if Int(60 / interval) < 300 && Int(60 / interval) > 30 { // heuristic: BPM shouldn't be less than 30 or greater than 300 because that's very unlikely
                        measuredBPM = Int(60 / interval)
                    }
                    if previousBPM! == 0 {
                        previousBPM = measuredBPM
                    }
                    let difference = measuredBPM - previousBPM!
                    if difference > -5 && difference < 5 { // Two consistent reads means we're probably good. Accept.
                        validBPM = (measuredBPM + previousBPM!)/2
                    }
                    
                    previousBPM = measuredBPM
                    
                    DispatchQueue.main.async {
                        self.BPMText.text = String(self.validBPM!) + " BPM"
                        if self.validBPM! > 100 {
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
                
                beginningTime = obsTime?[i]
            
            }
            previous = states[i]
        }
    }

    
    func useCaptureOutputForHeartRateEstimation(mean: Double, bytesPerRow: Int) {
        stateCount = 0
        let pixels = 1080 * bytesPerRow
        stateQueue?.addValue(value: mean/Double(pixels))
        if (observation!.count == 0) {
            self.lastCalculated = Date()
        }
        if (stateQueue?.getState() != -1) {
            obsTime!.append(NSDate().timeIntervalSince1970)
            observation!.append((stateQueue?.getState())!)
        }
        let since = Date().timeIntervalSince(self.lastCalculated!)
        if (since >= 3.0) {
            //        *** 2 state matrices -- leave in for later use
            //            let trans = [[0.6773,0.3227],[0.0842,0.9158]]
            //            let emit = [[0.7689,0.0061,0.1713,0.0537],
            //                        [0.0799,0.6646,0.1136,0.1420]]
            //            let p = [0.2, 0.8]
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
            
            self.calculate(states: self.viterbi(obs:self.observation!, trans:trans, emit:emit, states:states, initial:p).1, since: since)
            observation!.removeAll()
            obsTime!.removeAll()
        }
    }

    func writeCSV(){
        let fileName = "data.csv"
        let path = NSURL(fileURLWithPath: NSTemporaryDirectory()).appendingPathComponent(fileName)
        var csvText = "Observation,State\n"
        // What to write?
        do {
            try csvText.write(to: path!, atomically: true, encoding: String.Encoding.utf8)
        } catch {
            print("Failed to create file")
        }
        
        if MFMailComposeViewController.canSendMail() {
            let emailController = MFMailComposeViewController()
            emailController.mailComposeDelegate = self
            emailController.setToRecipients([])
            emailController.setSubject("Our CSV Data")
            emailController.setMessageBody("Please see the attachment!", isHTML: false)
            do {
                try emailController.addAttachmentData(Data(contentsOf: path!), mimeType: "text/csv", fileName: "data.csv")
            } catch {
                print("Failed to add attachment")
            }
            present(emailController, animated: true, completion: nil)
        }
        
        func mailComposeController(controller: MFMailComposeViewController, didFinishWithResult result: MFMailComposeResult, error: NSError?) {
            controller.dismiss(animated: true, completion: nil)
        }
    }
}
