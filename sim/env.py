import numpy as np
import matplotlib.pyplot as plt
from utils import choice, possible_directions, distance_enemies_around, position_from_direction
from utils.rewards import sparse_reward, full_reward

__all__ = ["Env"]


class Env:
    """
    Environment. An agent takes 1 pixel in the board
    """

    agent_radius = 1
    noise = 0.01
    max_length_episode = 50
    current_iter = 0

    def __init__(self, width, height, reward_type='full'):
        """
        Args:
            width: width of the board
            height: height of board
            reward_type (str): (full|sparse). Use default reward functions in utils.rewards. Defaults to full
        """
        assert reward_type in ['full', 'sparse'], "Unknown reward type."

        plt.ion()
        plt.show()

        self.width = width
        self.height = height
        self.agents = []
        self.initial_positions = []
        self.reward_function = sparse_reward if reward_type == 'sparse' else full_reward
        self.has_finished = False

    def random_position(self):
        return np.random.randint(0, self.width), np.random.randint(0, self.height)

    def add_agent(self, agent, position=None):
        self.initial_positions.append(position)
        agent.set_size_board(self.width, self.height)
        self.agents.append(agent)

    def set_position(self, agent, position=None):
        for k, other_agents in enumerate(self.agents):
            if agent == other_agents:
                self.initial_positions[k] = position

    def reset(self):
        self.current_iter = 0
        self.has_finished = False
        positions = []
        for k, agent in enumerate(self.agents):
            agent.reset()  # resets agents
            # Resets original positions (either fixed or random)
            position = self.initial_positions[k]
            position = self.random_position() if position is None else position
            positions.append(position)
            agent.set_position(position)
        return positions

    def give_rewards(self):
        """
        Gives reward to all agents
        """
        rewards = self.reward_function(self.agents, self.current_iter)
        for k, reward in enumerate(rewards):
            self.agents[k].set_reward(reward)
        return rewards

    def step(self):
        self.current_iter += 1
        terminal_state = False if self.max_length_episode is None else self.current_iter >= self.max_length_episode
        actions = []
        positions = []
        observations = self.agents[:]
        for agent in observations:
            for other_agent in observations:
                if agent.type == 'target' and other_agent.type == 'officer':
                    num_officers_around = len(distance_enemies_around(agent, observations, max_distance=1))
                    if num_officers_around >= 2:
                        terminal_state = True
            action = agent.draw_action(observations)
            actions.append(action)
            if np.random.rand() < self.noise:
                # We select a position at random and not the one selected
                action = choice(possible_directions(agent.limit_board, agent.position))
            next_position = position_from_direction(agent.position, action)
            # new_x, new_y = next_position
            # if new_x >= self.width or new_y >= self.height or new_x < 0 or new_y < 0:
            #     terminal_state = True
            agent.set_position(next_position)
            positions.append(agent.position)
            agent.add_to_history(action, observations)

        terminal_state, self.has_finished = self.has_finished, terminal_state

        # Give rewards
        rewards = self.give_rewards()
        return positions, actions, rewards, terminal_state

    def draw_board(self):
        plt.figure(0)
        plt.clf()
        plt.ylim(bottom=0, top=self.height)
        plt.xlim(left=0, right=self.width)
        plt.grid(True)
        for agent in self.agents:
            agent.plot(self.agent_radius)

        plt.draw()
        plt.pause(0.0001)
