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
    @IBOutlet var label: UILabel!
    var session : AVCaptureSession?
    var stateQueue : YChannelStateQueue?
    var heartRates : [Int]?
    
    var observation : [Int]?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        initializeCamera()
        observation = [Int]()
        heartRates = [Int]()
        self.label.text = "hi"
        // Do any additional setup after loading the view, typically from a nib.
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    func initializeCamera() {
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
            session!.startRunning()
            stateQueue = YChannelStateQueue()
            
        } catch let error as NSError {
            NSLog("\(error)")
        }
        
    }
    
    func captureOutput(_ captureOutput: AVCaptureOutput!, didOutputSampleBuffer sampleBuffer: CMSampleBuffer!, from connection: AVCaptureConnection!) {
        let buffer : CVPixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer)!
        CVPixelBufferLockBaseAddress(buffer, CVPixelBufferLockFlags(rawValue: CVOptionFlags(0)))
        
        let baseAddress = CVPixelBufferGetBaseAddressOfPlane(buffer, 0)
        let pointer = baseAddress?.assumingMemoryBound(to: UInt8.self)
        let bytesPerRow = CVPixelBufferGetBytesPerRowOfPlane(buffer, 0)
        let byteBuffer = UnsafeMutablePointer<UInt8>(pointer)!
        var sum = 0
        let pixels = 1080 * bytesPerRow
        for index in 0...pixels-1 {
            sum += Int(byteBuffer[index])
        }
        stateQueue?.addValue(value: Double(sum)/Double(pixels))
        
        if (stateQueue?.getState() != -1) {
            observation!.append((stateQueue?.getState())!)
        }
        
        if (observation!.count == 90) {
            //            let trans = [[0.6773,0.3227],[0.0842,0.9158]]
            let trans = [[0.6794, 0.3206, 0.0, 0.0],
                         [0.0, 0.5366, 0.4634, 0.0],
                         [0.0, 0.0, 0.3485, 0.6516],
                         [0.1508, 0.0, 0.0, 0.8492]]
            //            let emit = [[0.7689,0.0061,0.1713,0.0537],
            //                        [0.0799,0.6646,0.1136,0.1420]]
            let emit = [[0.6884, 0.0015, 0.3002, 0.0099],
                        [0.0, 0.7205, 0.0102, 0.2694],
                        [0.2894, 0.3731, 0.3362, 0.0023],
                        [0.0005, 0.8440, 0.0021, 0.1534]]
            
            //            let p = [0.2, 0.8]
            let p = [0.25, 0.20, 0.10, 0.45]
            let states = [0,1,2,3]
            
            // 4 obs, increasing, decreasing, local max and local min
            print(observation!)
            print(viterbi(obs:observation!, trans:trans, emit:emit, states:states, initial:p))
            print(calculate(states: viterbi(obs:observation!, trans:trans, emit:emit, states:states, initial:p).1))
            print(heartRates!)
            //            setLabelText(text: String(calculate(states: viterbi(obs:observation!, trans:trans, emit:emit, states:states, initial:p).1)))
            self.calculate(states: self.viterbi(obs:self.observation!, trans:trans, emit:emit, states:states, initial:p).1)
            if (self.heartRates!.count >= 10) {
                DispatchQueue.main.async {
                    self.label!.text = String(self.heartRates![self.heartRates!.count/2])
                }
            }
            
            
            
            //            label.text = String(calculate(states: viterbi(obs:observation!, trans:trans, emit:emit, states:states, initial:p).1))
            let calendar = NSCalendar.current
            let seconds = calendar.component(.second, from: NSDate() as Date)
            observation!.removeAll()
        }
        
    }
    
    
    
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
                
                //
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
        //print(vit)
        //print(path)
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
    
    func calculate(states:Array<Int>)->Int{
        //        let startSt = states[0]
        //        var firstEndState = 0
        //        var secondEndState = 0
        //        var meetSecondStart = false
        //        for i in 0..<states.count{
        //
        //            if states[i] != startSt && firstEndState==0{
        //                firstEndState = i
        //            }
        //
        //            else if states[i] == startSt && firstEndState != 0{
        //                meetSecondStart = true
        //            }
        //            if meetSecondStart && states[i] != startSt{
        //                secondEndState = i
        //                let heartRate = 60.0/(Double(secondEndState - firstEndState + 1)/50.0)
        //                return Int(heartRate)
        //            }
        //
        //        }
        
        var first2 = -1
        var second2 = -1
        var firstEst = true
        var lastSeen2 = false
        for i in 0..<states.count {
            if (states[i] == 2 && first2 == -1) {
                first2 = i
                lastSeen2 = true
            } else if (states[i] == 2 && first2 != -1 && !lastSeen2) {
                second2 = i
                if (!firstEst) {
                    self.heartRates!.append(Int(60.0/((Double(second2 - first2 + 1)/90.0)*3.0)))
                    self.heartRates!.sort()
                } else {
                    firstEst = false
                }
                print("first2", first2, "second2", second2)
                first2 = i
                second2 = -1
                lastSeen2 = true
            } else if (states[i] != 2) {
                lastSeen2 = false
            }
        }
        
        
        return 0
        
    }
    
    
}

