//
//  YChannelStateQueue.swift
//  CameraTest
//
//  Holds 3 brightness values in order to calculate whether they together form a
//  rising trend, falling trend, local minimum, or local maximum.

import UIKit

class YChannelStateQueue: NSObject {
    var valuesArray : [Double]?
    
    override init() {
        super.init()
        valuesArray = [Double]()
    }
    
    func addValue(value : Double) {
        if (valuesArray!.count >= 3) { // Should only ever reach 3
            _ = valuesArray!.popLast() // "_ =" is to silence a warning from Xcode about the result of popLast() being unused.
        }
        valuesArray!.insert(value, at: 0)
    }
    
    func getState() -> Int {
        // These are arbitrary numbers and I'm not sure if my labels for rising/falling/min/max are correct.
        if valuesArray!.count < 3 {
            return -1 // not enough measurements yet
        }
        if valuesArray![0] >= valuesArray![1] && valuesArray![1] >= valuesArray![2] {
            return 0; // rising
        }
        if valuesArray![0] <= valuesArray![1] && valuesArray![1] <= valuesArray![2] {
            return 1; // falling
        }
        if valuesArray![0] <= valuesArray![1] && valuesArray![1] >= valuesArray![2] {
            return 2; // local minimum
        }
        if valuesArray![0] >= valuesArray![1] && valuesArray![1] <= valuesArray![2] {
            return 3; // local maximum
        }
        
        return -1; // should never get here
    }

}
