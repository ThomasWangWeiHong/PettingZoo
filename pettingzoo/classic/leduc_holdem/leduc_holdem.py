from pettingzoo import AECEnv
from gym import spaces
import rlcard
from rlcard.utils.utils import print_card
import numpy as np

class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self,**kwargs):
        super(env, self).__init__()
        self.env = rlcard.make('leduc-holdem',**kwargs)
        self.num_agents = 2
        self.agents = list(range(self.num_agents))
        
        self.reset()

        self.observation_spaces = dict(zip(self.agents, [spaces.Box(low=0.0, high=1.0, shape=(34,), dtype=np.bool) for _ in range(self.num_agents)]))
        self.action_spaces = dict(zip(self.agents, [spaces.Discrete(self.env.game.get_action_num()) for _ in range(self.num_agents)]))

    def _convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def _decode_action(self, action):
        return self.env._decode_action(action)

    def observe(self, agent):
        obs = self.env.get_state(agent)
        return obs['obs']   

    def step(self, action, observe=True):
        obs, next_player_id = self.env.step(action)
        self.agent_selection = next_player_id
        self.dones = self._convert_to_dict([True if self.env.is_over() else False for _ in range(self.num_agents)])
        self.infos[next_player_id]['legal_moves'] = obs['legal_actions']
        if self.env.is_over():
            self.rewards = self._convert_to_dict(self.env.get_payoffs())
        else:
            self.rewards = self._convert_to_dict(np.array([0.0, 0.0]))
        if observe:
            return obs['obs']
        else:
            return

    def reset(self, observe=True):
        obs, player_id = self.env.init_game()
        self.agent_selection = player_id
        self.agent_order = [player_id, 0 if player_id==1 else 1]
        self.rewards = self._convert_to_dict(np.array([0.0, 0.0]))
        self.dones = self._convert_to_dict([False for _ in range(self.num_agents)])
        self.infos = self._convert_to_dict([{'legal_moves': []} for _ in range(self.num_agents)])
        self.infos[player_id]['legal_moves'] = obs['legal_actions']
        if observe:
            return obs['obs']
        else:
            return

    def render(self, mode='human'):
        state = self.env.get_perfect_information()
        print("\n=============== Player {}'s Hand ===============".format(self.agent_selection))
        print_card(state['hand_cards'][self.agent_selection])
        print('\n================= Public Cards =================')
        print_card(state['public_card']) if state['public_card'] != None else print('No public cards.')
        print('\n')
