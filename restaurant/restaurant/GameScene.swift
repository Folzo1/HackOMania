import SpriteKit

class GameScene: SKScene {
    var character: SKSpriteNode!
    var housenoroof: SKSpriteNode!
    var houseleftroof: SKSpriteNode!
    var houserightroof: SKSpriteNode!
    var boolState: Bool = false
    var background: SKSpriteNode!
    
    var targetPosition: CGPoint? // Stores the target position for the character
    let characterSpeed: CGFloat = 300.0 // Speed in points per second
    
    var showSavedRecipes: (() -> Void)? // Callback to SwiftUI
    
    private var isNearHouse: Bool = false // Flag to prevent multiple triggers
    
    override func didMove(to view: SKView) {
        // Set up the background
        let backgroundTexture = SKTexture(imageNamed: "background")
        backgroundTexture.filteringMode = .nearest
        background = SKSpriteNode(texture: backgroundTexture)
        background.position = CGPoint(x: size.width / 2, y: size.height / 2)
        background.zPosition = -1 // Ensure it's behind other nodes
        background.size = CGSize(width: size.width, height: size.height)
        addChild(background)
        
        // Set up the character
        let characterTexture = SKTexture(imageNamed: "character")
        characterTexture.filteringMode = .nearest // Preserve pixel quality
        character = SKSpriteNode(texture: characterTexture)
        character.position = CGPoint(x: size.width / 2, y: size.height / 2)
        character.setScale(3.5) // Scale up the character (e.g., 4x for 64x64 pixels)
        character.zPosition = 1 // Ensure the character is above the background but below the finger
        
        // Set up the physics body for the character
        character.physicsBody = SKPhysicsBody(texture: characterTexture, size: CGSize(width: 16, height: 16)) // Use original size for physics
        character.physicsBody?.isDynamic = true // Allow physics to affect the character
        character.physicsBody?.affectedByGravity = false // Disable gravity
        character.physicsBody?.allowsRotation = false // Prevent rotation
        character.physicsBody?.linearDamping = 10.0 // Increase friction to stop immediately
        character.physicsBody?.restitution = 0.0 // Prevent bouncing
        addChild(character)
        
        // Set up the target object (collision item)
        let housenoroofTexture = SKTexture(imageNamed: "housenoroof")
        housenoroofTexture.filteringMode = .nearest
        housenoroof = SKSpriteNode(texture: housenoroofTexture)
        housenoroof.position = CGPoint(x: size.width * 0.87, y: size.height * 0.79)
        housenoroof.setScale(2)
        housenoroof.physicsBody = SKPhysicsBody(texture: housenoroof.texture!, size: housenoroof.size) // Add physics body
        housenoroof.physicsBody?.isDynamic = false // Prevent gravity from affecting it
        housenoroof.physicsBody?.categoryBitMask = 1 // Set category for collision
        housenoroof.physicsBody?.contactTestBitMask = 2 // Set contact test mask
        addChild(housenoroof)
        
        // Set up the target object (collision item)
        let houseleftroofTexture = SKTexture(imageNamed: "houseleftroof")
        houseleftroofTexture.filteringMode = .nearest
        houseleftroof = SKSpriteNode(texture: houseleftroofTexture)
        houseleftroof.position = CGPoint(x: size.width * 0.23, y: size.height * 0.65)
        houseleftroof.setScale(2.4)
        houseleftroof.physicsBody = SKPhysicsBody(texture: houseleftroof.texture!, size: houseleftroof.size) // Add physics body
        houseleftroof.physicsBody?.isDynamic = false // Prevent gravity from affecting it
        houseleftroof.physicsBody?.categoryBitMask = 1 // Set category for collision
        houseleftroof.physicsBody?.contactTestBitMask = 2 // Set contact test mask
        addChild(houseleftroof)
        
        let houserightroofTexture = SKTexture(imageNamed: "houserightroof")
        houserightroofTexture.filteringMode = .nearest
        houserightroof = SKSpriteNode(texture: houserightroofTexture)
        houserightroof.position = CGPoint(x: size.width * 0.5, y: size.height * 0.17)
        houserightroof.setScale(2.40)
        houserightroof.physicsBody = SKPhysicsBody(texture: houserightroof.texture!, size: houserightroof.size) // Add physics body
        houserightroof.physicsBody?.isDynamic = false // Prevent gravity from affecting it
        houserightroof.physicsBody?.categoryBitMask = 1 // Set category for collision
        houserightroof.physicsBody?.contactTestBitMask = 2 // Set contact test mask
        addChild(houserightroof)
        
        // Set up physics world contact delegate
        physicsWorld.contactDelegate = self
    }
    
    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first else { return }
        let location = touch.location(in: self)
        
        // Set the target position for the character
        let offset: CGFloat = 50 // Adjust this value to control the distance between the finger and the character
        targetPosition = CGPoint(x: location.x, y: location.y - offset)
    }
    
    override func update(_ currentTime: TimeInterval) {
        // Check if the character is near any of the houses
        if isCharacterNearHouse(){
            isNearHouse = true // Set the flag to true
            
            // REPLACE THIS WITH SAVED VIEW
            showSavedRecipes?() // Call the callback to show the modal sheet
        } else if !isCharacterNearHouse() {
            isNearHouse = false // Reset the flag if the character moves away
        }
        
        // Move the character toward the target position at a constant speed
        if let targetPosition = targetPosition {
            // Calculate the distance between the character and the target position
            let offset = CGPoint(x: targetPosition.x - character.position.x,
                                 y: targetPosition.y - character.position.y)
            let distance = sqrt(offset.x * offset.x + offset.y * offset.y)
            
            // If the target is less than 5 pixels away, move directly to the target
            if distance <= 5 {
                character.position = targetPosition
                self.targetPosition = nil // Clear the target position
                character.physicsBody?.velocity = CGVector.zero // Stop all movement
            } else {
                // Calculate the movement vector
                let direction = CGPoint(x: offset.x / distance,
                                        y: offset.y / distance)
                let velocity = CGPoint(x: direction.x * characterSpeed,
                                       y: direction.y * characterSpeed)
                
                // Apply velocity to the character
                character.physicsBody?.velocity = CGVector(dx: velocity.x, dy: velocity.y)
            }
        }
    }
    
    // Check if the character is near any of the houses
    func isCharacterNearHouse() -> Bool {
        let houses = [housenoroof, houseleftroof, houserightroof]
        for house in houses {
            if let house = house {
                let offset = CGPoint(x: house.position.x - character.position.x,
                                     y: house.position.y - character.position.y)
                let distance = sqrt(offset.x * offset.x + offset.y * offset.y)
                if distance <= 100 { // Adjust this value as needed
                    return true
                }
            }
        }
        return false
    }
    
    func resetCharacterPosition() {
        // Reset character to center position
        character.position = CGPoint(x: size.width / 2, y: size.height / 2)
        targetPosition = nil
        character.physicsBody?.velocity = .zero
        isNearHouse = false
    }
}

extension GameScene: SKPhysicsContactDelegate {
    func didBegin(_ contact: SKPhysicsContact) {
        // Check if the contact involves the character and the target object
        if (contact.bodyA.node == character && contact.bodyB.node == housenoroof) ||
            (contact.bodyA.node == housenoroof && contact.bodyB.node == character) {
            print("no chimney collided") // Print to console
        } else if (contact.bodyA.node == character && contact.bodyB.node == houseleftroof) ||
                    (contact.bodyA.node == houseleftroof && contact.bodyB.node == character){
            
            print("left chimney collided") // Print to console
            
        } else if (contact.bodyA.node == character && contact.bodyB.node == houserightroof) ||
                    (contact.bodyA.node == houserightroof && contact.bodyB.node == character) {
            
            print("right chimney collided") // Print to console
            
        }
    }
}
