import numpy as np 

#MAX_TIME = float('inf')
MAX_TIME = 99999999
TX_per_blk = 1

class Node(object):
	def __init__(self, id_num, l, delta, isBad=False):
		self.id = id_num
		self.l = l
		self.isBad = isBad
		self.delta = delta
		self.committee = None
		self.num_communication = 0
		self.num_blocks = 0
	def mine_time(self, num_blocks=1):
		return np.random.exponential(1.0/self.l, num_blocks)
	def comm_time(self, force=False):
		if self.isBad and not force:
			return MAX_TIME
		self.num_communication += 1
		return np.random.uniform(0, self.delta, 1)[0]
	def make_bad(self):
		self.isBad = True
	def make_good(self):
		self.isBad = False
	def assign_committee(self, comm_id):
		self.committee = comm_id
	def get_num_communication(self):
		return self.num_communication
	def is_bad(self):
		return self.isBad
	def incr_block_count(self):
		self.num_blocks += 1
	def clear(self):
		self.committee = None
		# self.num_communication = 0
		# self.num_blocks = 0


class Committee(object):
	def __init__(self, id_num, c, delta):
		self.id = id_num
		self.min_size = c
		self.max_size = 1.1 * c
		self.curr_size = 0
		self.nodes = []
		self.delta = delta
		self.lead_id = None
		self.num_blocks_thru = 0

	def add_node(self, node):
		if self.curr_size >= self.max_size:
			#print("ERROR: committee full")
			return -1
		for n in self.nodes:
			if n.id == node.id:
				print("ERROR: node is already in committee!")
				return -2
		self.nodes.append(node)
		self.curr_size += 1
		return 0

	def remove_node(self, node):
		for n in self.nodes:
			if n.id == node.id:
				self.nodes.remove(node)
				self.curr_size -= 1
				return
		print("ERROR: node is not in committee!")
		return

	def clear(self):
		self.nodes = []
		self.curr_size = 0
		self.lead_id = None

	def full(self):
		return self.curr_size >= self.min_size

	def get_leader_id(self):
		lead_idx = self.get_new_leader()
		lead_time = self.nodes[lead_idx].comm_time()
		time1 = np.min(lead_time, self.delta)
		while lead_time > self.delta:
			#view_change
			comm_times = []
			for i in range(self.curr_size):
				n = self.nodes[i]
				if i != lead_idx:
					comm_times.append(n.comm_time())
			times_sorted = np.sort(comm_times)
			cutoff = times_sorted[(2.0 * self.min_size / 3.0) - 1]
			time1 += cutoff
			lead_idx = self.get_new_leader()
			lead_time = self.nodes[lead_idx].comm_time()
			time1 += np.min(lead_time, self.delta)
		return lead_idx, time1

	def run_PBFT(self, num_blks=1, gen_blks=True):
		final_time = 0
		#print("ft: " + str(final_time))
		for iteration in range(num_blks):
			#print(self.curr_size)
			# get leader
			leader_idx, time1 = self.get_leader_id()
			leader = self.nodes[leader_idx]

			#pre-prepare phase
			comm_times1 = [leader.comm_time() for i in range(self.curr_size - 1)]
			#comm_times1 = np.concatenate(comm_times1)
			#print(comm_times1)
			comm_times1 = np.insert(comm_times1, leader_idx, 0)
			#print(comm_times1)

			#prepare phase
			comm_times2 = []
			for i in range(self.curr_size):
				#print(comm_times2)
				receive_times = []
				size = 0
				for j in range(self.curr_size):
					#print(receive_times)
					if j != leader_idx and j != i:
						receive_times.append(self.nodes[j].comm_time() + comm_times1[j])
						size += 1
				#receive_times = np.concatenate(receive_times)
				#print(receive_times)
				sorted_times = np.sort(receive_times)
				#print(sorted_times)
				time = sorted_times[(2.0 * size / 3.0) - 1]
				#print(time)
				#print(time)
				comm_times2.insert(i,time)
			#comm_times2 = np.concatenate(comm_times2)

			#commit phase
			comm_times3 = []
			for i in range(self.curr_size):
				#print(comm_times3)
				receive_times = []
				size = 0
				for j in range(self.curr_size):
					if j != i:
						receive_times.append(self.nodes[j].comm_time() + comm_times2[j])
						size += 1
				sorted_times = np.sort(receive_times)
				time = sorted_times[(2.0 * size / 3.0) - 1]
				comm_times3.insert(i,time)

			#comm_times3 = np.concatenate(comm_times3)
			sorted_final_times = np.sort(comm_times3)
			time_required = sorted_final_times[(2.0 * self.min_size / 3.0) - 1] + time1
			final_time += time_required

			#print()
			if gen_blks:
				self.num_blocks_thru += 1
				for n in self.nodes:
					#print("hhhh")
					n.incr_block_count()

		#print("FT: " + str(final_time))
		return final_time

	def get_member_ids(self):
		arr = []
		for n in self.nodes:
			arr.append(n.id)
		return arr

	def get_size(self):
		return self.curr_size

	def get_new_leader(self):
		idx = np.random.randint(0,self.curr_size)
		while idx == self.lead_id:
			idx = np.random.randint(0,self.curr_size)
		self.lead_id = idx
		return idx

	def get_num_blks_thru(self):
		return self.num_blocks_thru


class Elastico(object):
	directories_comm = 0
	final_comm = 1
	def __init__(self, n, c, s, lambda_0, beta, delta, blks_per_epoch, protocol, attack=False):
		# n = number of nodes
		# c = size of committees
		# s = number of committees
		# lambda_0 = total hash power
		# beta = fraction of adversarial nodes
		# delta = max network delay
		# protocol = protocol used in each committee
		if s < 3:
			print("ERROR: need more than 2 committees")
		self.n = n
		self.c = c
		self.s = s
		self.lambda_0 = lambda_0
		self.beta = beta
		self.delta = delta
		self.bpe = blks_per_epoch
		self.protocol = protocol
		self.attack = attack
		self.nodes = []
		self.nodes_active = []
		self.committees = []

		# create nodes
		for i in range(n):
			l = lambda_0 / n
			self.nodes.append(Node(i,l,delta))

		# create adversarial nodes
		if attack:
			for j in range(int(beta * n)):
				self.nodes[j].make_bad()

		# create committees
		for j in range(s):
			self.committees.append(Committee(j,c,delta))


	def get_committee_assignment(self):
		return np.random.randint(1,self.s)

	def committees_full(self):
		for comm in self.committees:
			if not comm.full():
				return False
		return True

	def get_identities(self):
		# each node does a PoW
		times = [x.mine_time() for x in self.nodes]
		times = np.concatenate(times)
		#print(times)
		#times = np.array(times)
		#print(times)
		sorted_times = np.sort(times)
		#print(sorted_times)
		sorted_times = list(sorted_times)
		times = list(times)

		time_to_fill = 0
		for i in range(self.n):
			t = sorted_times[i]
			#idx = np.where(times == t)
			idx = times.index(t)
			#print(idx)
			if i < self.c:
				# first c members go to directory committee
				comm_id = 0
			else:
				comm_id = self.get_committee_assignment()
			flag = self.committees[comm_id].add_node(self.nodes[idx])
			while(flag != 0):
				comm_id = self.get_committee_assignment()
				flag = self.committees[comm_id].add_node(self.nodes[idx])
			self.nodes[idx].assign_committee(comm_id)
			self.nodes_active.append(self.nodes[idx])

			# stop once committees are full
			if self.committees_full():
				time_to_fill = t
				break
		if not self.committees_full():
			self.clear()
			return self.get_identities()

		return time_to_fill

	def broadcast_committees(self):
		# directory members announce themselves
		directory_ids = self.committees[0].get_member_ids()

		broadcast_time = []
		for n in self.nodes:
			comm_times = [self.nodes[i].comm_time(force=True) for i in directory_ids]
			#print(comm_times)
			#comm_times = np.concatenate(comm_times)
			comm_sorted = np.sort(comm_times)
			#print(comm_sorted)
			size = self.committees[0].get_size()
			#print(size)
			broadcast_time.append(comm_sorted[(2.0 * size / 3.0) - 1])

		# print("here")
		#print(broadcast_time)
		time1 = np.max(broadcast_time)
		#print(time1)
		#print(time1)
		#print(time1)

		# all other members announce themselves to directory committee
		time2 = -1.0
		for i in range(1,self.s):
			member_ids = self.committees[i].get_member_ids()
			times = [self.nodes[m].comm_time(force=True) for m in member_ids]
			#times = np.concatenate(times)
			max_time = np.max(times)
			# print(times)
			# print(max_time)
			if max_time > time2:
				time2 = max_time
		#print(time2)

		# directory connects shards to themselves
		time3 = -1.0
		for j in range(1,self.s):
			comm = self.committees[j]
			for i in range(comm.get_size()):
				connect_times = [self.nodes[d].comm_time() for d in directory_ids]
				#print(connect_times)
				#connect_times = np.concatenate(connect_times)
				sorted_times = np.sort(connect_times)
				#print(sorted_times)
				cutoff = sorted_times[(2.0 * self.c / 3.0) - 1]
				if cutoff > time3:
					time3 = cutoff

		total_time = time1 + time2 + time3
		# print(time1)
		# print(time2)
		# print(time3)
		return total_time

	def intra_committee_consensus(self):
		if self.protocol == "PBFT":
			times = [self.committees[i].run_PBFT(self.bpe, gen_blks=True) for i in range(2,self.s)]
			#times = np.concatenate(times)
			#print(times)
			return np.max(times)
		else:
			print("ERROR: only PBFT protocol implemented!")

	def final_consensus(self):
		time = self.committees[1].run_PBFT(num_blks=1, gen_blks=False)
		#print(time)
		return time

	def generate_epoch_rand(self):
		ids = self.committees[1].get_member_ids()
		#print(ids)
		#n = sel.committees[1].get_size()
		time1_arr = []
		for i in ids:
			times = []
			for j in ids:
				if i!=j:
					times.append(self.nodes[j].comm_time())
			sorted_times = np.sort(times)
			time1_arr.append(sorted_times[(2.0 * self.c / 3.0) - 1])
		#time1_arr = np.concatenate(time1_arr)
		#print(time1_arr)
		time1 = np.max(time1_arr)

		time2 = self.committees[1].run_PBFT(num_blks=1, gen_blks=False)
		#print(time2)

		time3_arr = []
		for n in self.nodes_active:
			#print(n.id)
			comm_times = [self.nodes[idx].comm_time() for idx in ids]
			#comm_times = np.concatenate(comm_times)
			sorted_times = np.sort(comm_times)
			time3_arr.append(sorted_times[(2.0 * self.c / 3.0) - 1])

		#print(time3_arr)
		final_time = np.max(time3_arr)
		self.clear()
		return final_time

	def clear(self):
		self.nodes_active = []
		for comm in self.committees:
			comm.clear()
		for n in self.nodes:
			n.clear()
		return

	def run_epochs(self, num_epochs=1):
		epoch_times = []
		for i in range(num_epochs):
			time1 = self.get_identities()
			time2 = self.broadcast_committees()
			time3 = self.intra_committee_consensus()
			time4 = self.final_consensus()
			time5 = self.generate_epoch_rand()
			time = time1 + time2 + time3 + time4 + time5
			epoch_times.append(time)
		return np.sum(epoch_times)

	def get_total_num_communication(self):
		total = 0
		for node in self.nodes:
			total += node.get_num_communication()
		return total

	def get_num_TXs(self):
		count_blks = 0
		for comm in self.committees:
			#print(count_blks)
			count_blks += comm.get_num_blks_thru()
		return count_blks * TX_per_blk

	def get_throuhgput(self):
		print("-------THROUGHPUT-------")
		time = self.run_epochs(10)
		print("Time: " + str(time))
		TX_count = self.get_num_TXs()
		print("TX Count: " + str(TX_count))
		throughput = float(TX_count) / time
		print("Throughput: " + str(throughput) + " TXs per second")
		print("")
		return throughput

	def get_communication_per_node(self):
		print("-------COMMUNICATION-------")
		count = self.get_total_num_communication()
		print("Number of Messages Sent: " + str(count))
		n = len(self.nodes)
		print("Number of Active Nodes: " + str(n))
		comm_per_node = float(count) / n
		print("Communication Per Node: " + str(comm_per_node) + " Messages per node")
		print("")
		return comm_per_node

	def print_all(self):
		# self.n = n
		# self.c = c
		# self.s = s
		# self.lambda_0 = lambda_0
		# self.beta = beta
		# self.delta = delta
		# self.bpe = blks_per_epoch
		# self.protocol = protocol
		# self.attack = attack
		# self.nodes = []
		# self.committees = []
		print("Number of Nodes (N): " + str(self.n))
		print("Minimum Size of Each Committe (C): " + str(self.c))
		print("# of Committees (S): " + str(self.s))
		print("Overall Hashing Power (lambda_0): " + str(self.lambda_0))
		print("Percentaeg Adversarial (Beta): " + str(self.beta))
		print("Max Netowrk Delay (Delta): " + str(self.delta))
		print("# of Blocks per Epoch: " + str(self.bpe))
		print("Protocol: " + str(self.protocol))
		print("Are We Similuating an Attack?: " + str(self.attack))
		print("")
		print("Nodes: ")

		for i in range(self.n):
			node = self.nodes[i]
			#print(str(i))
			print("ID: " + str(node.id) + "         Committee: " + str(node.committee) + "        Total number of messages sent: " + str(node.get_num_communication()))

		print("")
		print("Committees: ")
		print("")

		for i in range(self.s):
			comm = self.committees[i]
			print("Comm #" + str(i) + ": ")
			print("Member IDs: ")
			print(comm.get_member_ids())
			print("# of Blocks Committed: " + str(comm.get_num_blks_thru()))
			print("")
			#print(comm.get_num_blks_thru())




def run_experiment(n_vals, betas, c_vals):
	lambda_n = 1.0/100
	delta = 0.01
	bpe = 10
	protocol = "PBFT"

	throughputs = np.zeros((len(c_vals), len(betas), len(n_vals)))
	comms = np.zeros((len(c_vals), len(betas), len(n_vals)))

	for i, c in enumerate(c_vals):
		for j, b in enumerate(betas):
			for k, n in enumerate(n_vals):
				print("N = " + str(n) + "    Beta = " + str(b) + "    C = " + str(c))
				l_0 = lambda_n * n
				s = int((0.9 * n) / c)
				e = Elastico(n, c, s, l_0, b, delta, bpe, protocol, attack=False)
				val1 = e.get_throuhgput()
				val2 = e.get_communication_per_node()
				throughputs[i][j] = val1
				comms[i][j] = val2
				print("")

	print(throughputs)
	print(comms)


if __name__ == '__main__':
	n_vals = [500, 1000, 2000, 3000]
	betas = [0.1, 0.2]
	c_vals = [50, 100]
	run_experiment(n_vals, betas, c_vals)


