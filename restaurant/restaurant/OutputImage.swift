//
//  OutputImage.swift
//  restaurant
//
//  Created by Christopher on 15/2/25.
//

import Foundation

struct OutputImage: Identifiable, Codable {
    var id = UUID()
    var imgData: [Data] = []
}
