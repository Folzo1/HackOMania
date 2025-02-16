import SpriteKit

class GameScene: SKScene {
    var character: SKSpriteNode!
    var housenoroof: SKSpriteNode!
    var houseleftroof: SKSpriteNode!
    var houserightroof: SKSpriteNode!
    var boolState: Bool = false
    var background: SKSpriteNode!
    var animationTextures: [SKTexture] = []
    var walkAnimationAction: SKAction!
    var isAnimating = false
    
    var targetPosition: CGPoint?
    let characterSpeed: CGFloat = 300.0
    var showSavedRecipes: (() -> Void)?
    private var isNearHouse: Bool = false

    override func didMove(to view: SKView) {
        // Load animation frames
        animationTextures = (0...3).map { index in
            let texture = SKTexture(imageNamed: "character\(index)")
            texture.filteringMode = .nearest
            return texture
        }
        
        // Create animation action
        walkAnimationAction = SKAction.repeatForever(
            SKAction.animate(with: animationTextures, timePerFrame: 0.2)
        )

        // Set up background
        let backgroundTexture = SKTexture(imageNamed: "background")
        backgroundTexture.filteringMode = .nearest
        background = SKSpriteNode(texture: backgroundTexture)
        background.position = CGPoint(x: size.width/2, y: size.height/2)
        background.zPosition = -1
        background.size = CGSize(width: size.width, height: size.height)
        addChild(background)

        // Set up character with first animation frame
        character = SKSpriteNode(texture: animationTextures.first)
        character.position = CGPoint(x: size.width/2, y: size.height/2)
        character.setScale(3.5)
        character.zPosition = 1
        
        // Physics setup
        character.physicsBody = SKPhysicsBody(texture: animationTextures.first!,
                                            size: CGSize(width: 16, height: 16))
        character.physicsBody?.isDynamic = true
        character.physicsBody?.affectedByGravity = false
        character.physicsBody?.allowsRotation = false
        character.physicsBody?.linearDamping = 10.0
        character.physicsBody?.restitution = 0.0
        addChild(character)

        // House setup (unchanged from original)
        setupHouseNodes()
        physicsWorld.contactDelegate = self
    }

    private func setupHouseNodes() {
        // housenoroof setup
        let housenoroofTexture = SKTexture(imageNamed: "housenoroof")
        housenoroof = createHouseNode(texture: housenoroofTexture,
                                    position: CGPoint(x: size.width*0.87, y: size.height*0.79),
                                    scale: 2)
        
        // houseleftroof setup
        let houseleftroofTexture = SKTexture(imageNamed: "houseleftroof")
        houseleftroof = createHouseNode(texture: houseleftroofTexture,
                                       position: CGPoint(x: size.width*0.23, y: size.height*0.65),
                                       scale: 2.4)
        
        // houserightroof setup
        let houserightroofTexture = SKTexture(imageNamed: "houserightroof")
        houserightroof = createHouseNode(texture: houserightroofTexture,
                                       position: CGPoint(x: size.width*0.5, y: size.height*0.17),
                                       scale: 2.4)
    }

    private func createHouseNode(texture: SKTexture, position: CGPoint, scale: CGFloat) -> SKSpriteNode {
        texture.filteringMode = .nearest
        let node = SKSpriteNode(texture: texture)
        node.position = position
        node.setScale(scale)
        node.physicsBody = SKPhysicsBody(texture: texture, size: node.size)
        node.physicsBody?.isDynamic = false
        node.physicsBody?.categoryBitMask = 1
        node.physicsBody?.contactTestBitMask = 2
        addChild(node)
        return node
    }

    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first else { return }
        let location = touch.location(in: self)
        targetPosition = CGPoint(x: location.x, y: location.y - 50)
    }

    override func update(_ currentTime: TimeInterval) {
        handleHouseProximity()
        handleCharacterMovement()
        controlAnimation()
    }

    private func handleHouseProximity() {
        if isCharacterNearHouse() && !isNearHouse {
            isNearHouse = true
            showSavedRecipes?()
        } else if !isCharacterNearHouse() {
            isNearHouse = false
        }
    }

    private func handleCharacterMovement() {
        guard let targetPosition = targetPosition else { return }
        
        let offset = CGPoint(x: targetPosition.x - character.position.x,
                           y: targetPosition.y - character.position.y)
        let distance = sqrt(offset.x * offset.x + offset.y * offset.y)
        
        if distance <= 5 {
            character.position = targetPosition
            self.targetPosition = nil
            character.physicsBody?.velocity = .zero
        } else {
            let direction = CGPoint(x: offset.x/distance, y: offset.y/distance)
            let velocity = CGPoint(x: direction.x * characterSpeed, y: direction.y * characterSpeed)
            character.physicsBody?.velocity = CGVector(dx: velocity.x, dy: velocity.y)
        }
    }

    private func controlAnimation() {
        guard let velocity = character.physicsBody?.velocity else { return }
        let speed = sqrt(velocity.dx * velocity.dx + velocity.dy * velocity.dy)
        
        if speed > 5.0 {
            if !isAnimating {
                character.run(walkAnimationAction, withKey: "walking")
                isAnimating = true
            }
        } else {
            if isAnimating {
                character.removeAction(forKey: "walking")
                character.texture = animationTextures.first
                isAnimating = false
            }
        }
    }

    func isCharacterNearHouse() -> Bool {
        [housenoroof, houseleftroof, houserightroof].contains { house in
            guard let house = house else { return false }
            let dx = house.position.x - character.position.x
            let dy = house.position.y - character.position.y
            return (dx * dx + dy * dy) <= 10000 // 100^2
        }
    }

    func resetCharacterPosition() {
        character.position = CGPoint(x: size.width/2, y: size.height/2)
        targetPosition = nil
        character.physicsBody?.velocity = .zero
        isNearHouse = false
        
        if isAnimating {
            character.removeAction(forKey: "walking")
            character.texture = animationTextures.first
            isAnimating = false
        }
    }
}

extension GameScene: SKPhysicsContactDelegate {
    func didBegin(_ contact: SKPhysicsContact) {
        let collision = contact.bodyA.node == character ? contact.bodyB.node : contact.bodyA.node
        
        switch collision {
        case housenoroof:
            print("No chimney collision")
        case houseleftroof:
            print("Left chimney collision")
        case houserightroof:
            print("Right chimney collision")
        default:
            break
        }
    }
}
