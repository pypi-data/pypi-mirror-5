import logging
import random
import Pyro4
from pyage.core.agent import AGENT
from pyage.core.inject import Inject

logger = logging.getLogger(__name__)

class Pyro4Migration(object):
    @Inject("ns_hostname")
    def __init__(self):
        super(Pyro4Migration, self).__init__()

    def migrate(self, agent):
        try:
            if random.random() > 0.95 and len(agent.parent.get_agents()) > 1:
                logger.debug("migrating!")
                aggregate = self.__get_random_aggregate(agent)
                logger.debug(aggregate.get_address())
                aggregate.add_agent(agent.parent.remove_agent(agent))
        except:
            logging.exception("")

    def __get_random_aggregate(self, agent):
        ns = Pyro4.locateNS(self.ns_hostname)
        agents = ns.list(AGENT)
        logger.debug(agents)
        del agents[AGENT + "." + agent.parent.address]
        return Pyro4.Proxy(random.choice(agents.values()))


class NoMigration(object):
    def migrate(self, agent):
        pass