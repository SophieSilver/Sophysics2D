from Sophysics2D import *


def main():
	pygame.init()
	pygame.font.init()
	# This is a dummy application to test the functionality of Sophysics2D
	display = pygame.display.set_mode((1280, 720))
	pygame.display.set_caption("Sophysics 2D")
	consolas = pygame.font.SysFont("consolas", 16)

	rm = RenderManager(display, 1/80)
	rbm = RigidBodyManager()
	env = DefaultEnvironment(components=(rm, rbm))

	ball1_transform = Transform(pygame.Vector2(0, 0))
	grav_acc1 = ConstantAcceleration((0, -9.8))
	ball1 = get_circle_body(1, 1, 1, (255, 0, 0), 1, (ball1_transform, grav_acc1))
	grav_acc2 = ConstantAcceleration((0, -9.8))
	ball2 = get_circle_body(1, 1, radius=1, color=(0, 255, 0), layer=1, components=(grav_acc2,))
	border = get_border_object(4, -4, -7, 7, 1, Color.WHITE, 0)

	env.attach_object(ball1)
	ball1.get_component(RigidBody).body.velocity = pymunk.Vec2d(3, 4)
	env.attach_object(border)
	env.attach_object(ball2)
	env.start()
	running = True
	clock = pygame.time.Clock()

	rb1 = ball1.get_component(RigidBody)
	rb2 = ball2.get_component(RigidBody)

	while(running):
		clock.tick(60)
		for event in pygame.event.get():
			if(event.type == pygame.QUIT):
				running = False

		env.advance()
		env.render()
		# ball1_transform.position.x -= 0.01
		e1 = get_energy(rb1)
		e2 = get_energy(rb2)
		text = consolas.render(f"e1: {e1:.3}, e2: {e2:.3}, e_total: {e1 + e2:.3}", True, (0, 255, 0))
		display.blit(text, (0, 0))

		pygame.display.update()


def get_energy(obj: RigidBody):
	kin_energy = (obj.body.mass * obj.body.velocity.length ** 2) / 2
	pot_energy = obj.body.mass * 9.8 * (obj.sim_object.transform.position.y + 4)
	return pot_energy + kin_energy


if(__name__ == "__main__"):
	main()
