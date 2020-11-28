import os
import time

from stable_baselines.common.callbacks import BaseCallback
from rl_interaction.utils.utils import Timer
from loguru import logger


def collect_coverage(udid, package, coverage_dir, coverage_count):
    os.system(f'adb -s {udid} shell am broadcast -a edu.gatech.m3.emma.COLLECT_COVERAGE')
    # os.system(f'adb  shell am broadcast -p {package} -a intent.END_COVERAGE')
    os.system(f'adb -s {udid} pull /mnt/sdcard/coverage.ec {os.path.join(".", coverage_dir, str(coverage_count))}.ec')
    # os.system(f'adb -s {udid} pull /sdcard/Android/data/{package}/files/coverage.ec '
    #         f'{os.path.join(".", coverage_dir, str(coverage_count))}.ec')


class TimerCallback(BaseCallback):
    def __init__(self, timer, app, verbose=0):
        super(TimerCallback, self).__init__(verbose)
        self.timer = Timer(timer)
        self.app = app
        # Those variables will be accessible in the callback
        # (they are defined in the base class)
        # The RL model
        # self.model = None  # type: BaseRLModel
        # An alias for self.model.get_env(), the environment used for training
        # self.training_env = None  # type: Union[gym.Env, VecEnv, None]
        # Number of time the callback was called
        # self.n_calls = 0  # type: int
        # self.num_timesteps = 0  # type: int
        # local and global variables
        # self.locals = None  # type: Dict[str, Any]
        # self.globals = None  # type: Dict[str, Any]
        # The logger object, used to report things in the terminal
        # self.logger = None  # type: logger.Logger
        # # Sometimes, for event callback, it is useful
        # # to have access to the parent object
        # self.parent = None  # type: Optional[BaseCallback]

    def _on_training_start(self) -> None:
        """
        This method is called before the first rollout starts.
        """
        pass

    def _on_rollout_start(self) -> None:
        """
        A rollout is the collection of environment interaction
        using the current policy.
        This event is triggered before collecting new samples.
        """
        pass

    def _on_step(self) -> bool:
        """
        This method will be called by the model after each call to `env.step()`.

        For child callback (of an `EventCallback`), this will be called
        when the event is triggered.

        :return: (bool) If the callback returns False, training is aborted early.
        """
        if self.timer.timer_expired():
            logger.info(f'Timer expired at {self.num_timesteps}')
            self.app.coverage_count += 1
            collect_coverage(udid=self.app.udid, package=self.app.package, coverage_dir=self.app.coverage_dir,
                             coverage_count=self.app.coverage_count)
            return False
        elif self.app.instr:
            if (self.num_timesteps % 25) == 0:
                self.app.coverage_count += 1
                collect_coverage(udid=self.app.udid, package=self.app.package, coverage_dir=self.app.coverage_dir,
                                 coverage_count=self.app.coverage_count)
                return True
        else:
            return True

    def _on_rollout_end(self) -> None:
        """
        This event is triggered before updating the policy.
        """
        pass

    def _on_training_end(self) -> None:
        """
        This event is triggered before exiting the `learn()` method.
        """
        pass
