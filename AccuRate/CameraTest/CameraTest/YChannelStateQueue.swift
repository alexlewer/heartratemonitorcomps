//
//  YChannelStateQueue.swift
//  AccuRate
//
//  Created by Aidan Holloway-Bidwell, Lucy Lu, Grant Terrien, Renzhi Wu.
//

import UIKit

class YChannelStateQueue: NSObject {
    var valuesArray : [Double]?
    
    override init() {
        super.init()
        valuesArray = [Double]()
    }
    
    func addValue(value : Double) {
        if ((valuesArray?.count)! >= 3) { // Should only ever reach 3
            valuesArray?.popLast()
        }
        valuesArray?.insert(value, at: 0)
    }
    
    func getState() -> Int {
        // These are arbitrary numbers and I'm not sure if my labels for rising/falling/min/max are correct.
        if (valuesArray?.count)! < 3 {
            return -1 // not enough measurements yet
        }
        if valuesArray![0] >= valuesArray![1] && valuesArray![1] >= valuesArray![2] {
            return 0 // rising
        }
        if valuesArray![0] <= valuesArray![1] && valuesArray![1] <= valuesArray![2] {
            return 1 //falling
        }
        if valuesArray![0] <= valuesArray![1] && valuesArray![1] >= valuesArray![2] {
            return 2 // local maximum
        }
        if valuesArray![0] >= valuesArray![1] && valuesArray![1] <= valuesArray![2] {
            return 3 // local minimum
        }
        
        return -1 // hopefully don't get here
    }

}
