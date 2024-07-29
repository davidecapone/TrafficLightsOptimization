import random
from entities.car_actions import CarActions

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000

class TrafficMDP:
    '''
    TrafficMDP class that represents the Markov Decision Process for the traffic intersection.

    Attributes:
    - states: list of states in the MDP (S)
    - actions: list of actions in the MDP (A)
    - discount_factor: discount factor for the MDP (gamma)
    - theta: threshold for the policy evaluation
    - values: dictionary of state values (V)
    - policy: dictionary of state-action pairs (pi)
    '''
    def __init__(self):
        self.states = ['EW', 'NS']
        self.actions = ['maintain', 'change']
        self.discount_factor = 0.95
        self.theta = 0.01
        self.values = {state: 0 for state in self.states}
        self.policy = {
            'EW': {'maintain': 0.5, 'change': 0.5},
            'NS': {'maintain': 0.5, 'change': 0.5}
        }

    def get_reward(self, cars, action, state):
        '''
        Get the reward R(s, a) for a given state-action pair.

        Parameters:
        - cars: list of Car objects
        - action: action to take
        - state: actual state

        Returns:
        - reward: reward for the given state-action pair

        I the action is 'change', the reward is the average waiting time of stopped cars divided by the number of incoming cars where the stoplight is green.
        If the action is 'maintain', the reward is the number of incoming cars where the stoplight is green divided by the average waiting time of stopped cars.
        In this way, the reward is high when there are many incoming cars where the stoplight is green, and also when the the stopped cars have been waiting for a long time.
        '''
        if state == 'EW':
            stopped_cars = [car for car in cars if 
                            car.direction in [CarActions.UP, CarActions.DOWN]
                            and car.is_stopped()]
            incoming_cars = len([car for car in cars if 
                                 (car.x > WINDOW_WIDTH//2 and car.direction == CarActions.LEFT) 
                                 or (car.x < WINDOW_WIDTH//2 and car.direction == CarActions.RIGHT) 
                                 and not car.is_stopped()])
        else:
            stopped_cars = [car for car in cars if
                            car.direction in [CarActions.LEFT, CarActions.RIGHT]
                            and car.is_stopped()]
            incoming_cars = len([car for car in cars if (car.y > WINDOW_HEIGHT//2 and car.direction == CarActions.UP)
                                 or (car.y < WINDOW_HEIGHT//2 and car.direction == CarActions.DOWN)
                                 and not car.is_stopped()])

        avg_wait_time = sum(car.waiting_time//30 for car in stopped_cars) / len(stopped_cars) if stopped_cars else 0

        if action == 'change':
            return avg_wait_time / incoming_cars if incoming_cars > 0 else avg_wait_time
        else:
            return incoming_cars / avg_wait_time if avg_wait_time > 0 else incoming_cars
        
    def get_transition_probability(self, cars, action, state, next_state):
        '''
        Get the transition probability P(s', r| s, a) for a given state-action pair.

        Parameters:
        - cars: list of Car objects
        - action: action to take (a)
        - state: current state (s)
        - next_state: next state (s')

        Returns:
        - probability: transition probability P(s', r| s, a)

        The transition probability is 0 if the action is 'maintain' and s is different from s', or if the action is 'change' and s is the same as s'.
        Otherwise, the transition probability is 1 if the action is 'maintain' and the reward for maintaining is greater than the reward for changing,
        or if the action is 'change' and the reward for changing is greater than the reward for maintaining.
        In all other cases, the transition probability is 0.
        '''
        if action == 'maintain' and state != next_state:
            return 0
        elif action == 'change' and state == next_state:
            return 0
        
        change_reward = self.get_reward(cars, 'change', state)
        maintain_reward = self.get_reward(cars, 'maintain', state)

        if action == 'maintain' and maintain_reward > change_reward:
            return 1
        elif action == 'change' and change_reward > maintain_reward:
            return 1
        else:
            return 0

    def policy_evaluation(self, cars):
        '''
        Evaluate the policy using iterative policy evaluation.

        Parameters:
        - cars: list of Car objects

        This implementation follows the iterative policy evaluation algorithm on the Reinforcement Learning (Sutton, Barto) book.
        '''
        while True:
            delta = 0
            for state in self.states:
                v = self.values[state]

                new_value = 0
                for action in self.actions:
                    for state_ in self.states:
                        new_value += self.policy[state][action] * self.get_transition_probability(cars, action, state, state_) * (self.get_reward(cars, action, state) + self.discount_factor * self.values[state_])

                self.values[state] = new_value

                delta = max(delta, abs(v - self.values[state]))
            if delta < self.theta:
                return

    def policy_improvement(self, cars):
        '''
        Improve the policy using policy improvement.

        Parameters:
        - cars: list of Car objects

        Returns:
        - policy_stable: boolean indicating if the policy is stable

        This implementation follows the policy improvement algorithm on the Reinforcement Learning (Sutton, Barto) book.
        '''
        policy_stable = True
        for state in self.states:
            old_action = self.get_action(state)

            action_values = {action: 0 for action in self.actions}
            for state_ in self.states:
                action_values = {action: action_values[action] + (self.get_transition_probability(cars, action, state, state_) * (self.get_reward(cars, action, state_) + self.discount_factor * self.values[state_])) for action in self.actions}

            best_action = max(action_values, key=action_values.get)
            self.policy[state] = {action: 1 if action == best_action else 0 for action in self.actions}

            if old_action != best_action:
                policy_stable = False

        return policy_stable

    def policy_iteration(self, cars):
        '''
        Perform policy iteration.

        Parameters:
        - cars: list of Car objects

        This implementation follows the policy iteration algorithm on the Reinforcement Learning (Sutton, Barto) book.
        '''
        while True:
            self.policy_evaluation(cars)

            if self.policy_improvement(cars):
                return

    def get_action(self, state):
        '''
        Get the action to take in a given state.

        Parameters:
        - state: current state

        Returns:
        - action: action to take

        This method returns the action to take in a given state according to the policy (pi*(s)).
        '''
        return random.choices(self.actions, weights=[self.policy[state]['maintain'], self.policy[state]['change']])[0]
    
    def value_iteration(self, cars, current_state):
        '''
        Perform value iteration.

        Parameters:
        - cars: list of Car objects
        - current_state: current state

        Returns:
        - action: action to take

        This implementation follows the value iteration algorithm seen on the Reinforcement Learning (Sutton, Barto) book.
        '''
        while True:
            delta = 0
            new_values = {}
            for state in self.states:
                v = self.values[state]
                action_values = []
                for action in self.actions:
                    value_sum = 0
                    for state_ in self.states:
                        value_sum += self.get_transition_probability(cars, action, state, state_) * (self.get_reward(cars, action, state) + self.discount_factor * self.values[state_])
                    action_values.append(value_sum)

                new_values[state] = max(action_values)
                delta = max(delta, abs(v - new_values[state]))
            
            self.values = new_values

            if delta < self.theta:
                break

        action_values = []
        for action in self.actions:
            value_sum = 0
            for state_ in self.states:
                value_sum += self.get_transition_probability(cars, action, current_state, state_) * (self.get_reward(cars, action, current_state) + self.discount_factor * self.values[state_])
            action_values.append(value_sum)
                
        return self.actions[action_values.index(max(action_values))]