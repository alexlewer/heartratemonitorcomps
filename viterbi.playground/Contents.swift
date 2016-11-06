//: Playground - noun: a place where people can play

import UIKit

func viterbi(obs:Array<Int>, trans:Array<Array<Double>>, emit:Array<Array<Double>>, states: Array<Int>, initial:Array<Double>)->(Double, [Int]){
    
    var vit = [[Int:Double]()]
    var path = [Int:[Int]]()
    
    for s in states{
        vit[0][s] = trans[0][s] * emit[s][obs[0]]
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
    print(vit)
    print(path)
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



let trans = [[0.6773,0.3227],[0.0842,0.9158]]
let emit = [[0.7689,0.0061,0.1713,0.0537],
            [0.0799,0.6646,0.1136,0.1420]]
let p = [0.2, 0.8]
let states = [0,1]
// 4 obs, increasing, decreasing, local max and local min
print(viterbi(obs:[0,1,3,2,1,0,2,1], trans:trans, emit:emit, states:states, initial:p))


