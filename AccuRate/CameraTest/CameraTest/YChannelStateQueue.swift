//
//  YChannelStateQueue.swift
//  CameraTest
//
//  Created by Grant Terrien on 10/23/16.
//  Copyright © 2016 com.terrien. All rights reserved.
//

import UIKit

class YChannelStateQueue: NSObject {
    var valuesArray : [Double]?
    
    override init() {
        super.init()
        valuesArray = [Double]()
    }
    
    func addValue(value : Double) {
        if (valuesArray!.count >= 3) { // Should only ever reach 3
            valuesArray!.popLast()
        }
        valuesArray!.insert(value, at: 0)
    }
    
    func getState() -> (Int, Double) {
        // These are arbitrary numbers and I'm not sure if my labels for rising/falling/min/max are correct.
        if valuesArray!.count < 3 {
            return (-1, -1) // not enough measurements yet
        }
        if valuesArray![0] >= valuesArray![1] && valuesArray![1] >= valuesArray![2] {
            return (0, valuesArray![1]) // rising
        }
        if valuesArray![0] <= valuesArray![1] && valuesArray![1] <= valuesArray![2] {
            return (1, valuesArray![1]) //falling
        }
        if valuesArray![0] <= valuesArray![1] && valuesArray![1] >= valuesArray![2] {
            return (2, valuesArray![1]) // local minimum
        }
        if valuesArray![0] >= valuesArray![1] && valuesArray![1] <= valuesArray![2] {
            return (3, valuesArray![1]) // local maximum
        }
        
        return (-1, -1); // hopefully don't get here
    }

}
