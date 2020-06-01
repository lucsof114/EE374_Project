import numpy as np 

class Elastico(object):
	def __init__(self, n, lambda_0, beta, delta, c, protocol):
		# n = number of nodes
		# lambda_0 = total hash power
		# beta = fraction of adversarial nodes
		# delta = max network delay
		# c = size of committees
		# protocol = protocol used in each committee
		self.n = n
		self.lambda_0 = lambda_0
		self.beta = beta
		self.delta = delta
		self.c = c
		self.protocol = protocol

	def get_identities(self):
		# individual mining rates
		lambda_n = self.lambda_0 / self.n
		# time to complete POW
		pow_time = np.random.exponential(1.0/lambda_n, self.n)
		#time to communicate results
		comm_time = np.random.uniform(0, self.delta, self.n)
		# total time for this process is the max of the sums
		time = np.max(pow_time + comm_time)
		return time

	def broadcast_committees(self):
		# communication time
		comm_time = np.random.uniform(0, self.delta, self.n)
		time = np.max(comm_time)
		return time

	def intra_committee_consensus(self):
		if self.protocol == "PBFT":
			# do BFT
			num_comm = float(self.n) / self.c
			done_times = []
			for i in range(int(num_comm)):
				send_time = np.random.uniform(0, self.delta, self.c)
				receive_time = np.random.uniform(0, self.delta, self.c)
				total_time = send_time + receive_time
				sorted_time = np.sort(total_time)
				time_done = sorted_time[(self.c / 2.0)]
				done_times.append(time_done)
			time = np.max(done_times)
			return time

	def final_consensus(self):
		send_time = np.random.uniform(0, self.delta, self.c)
		receive_time = np.random.uniform(0, self.delta, self.c)
		total_time = send_time + receive_time
		sorted_time = np.sort(total_time)
		time = sorted_time[(self.c / 2.0)]
		return time

	def generate_epoch_rand(self):
		# broadcast random strings
		send_time = np.random.uniform(0, self.delta, self.c)
		time1 = np.max(send_time)
		# run consesus protocol
		send_time2 = np.random.uniform(0, self.delta, self.c)
		receive_time = np.random.uniform(0, self.delta, self.c)
		sum_time = send_time2 + receive_time
		sorted_sum_time = np.sort(sum_time)
		time2 = sorted_sum_time[(self.c / 2.0)]
		comm_time = np.random.uniform(0, self.delta, self.n * self.n)
		time3 = np.max(comm_time)
		return (time1+time2+time3)

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




def main():
	n_vals = [4, 16, 64, 256, 1024, 2048]
	lambda_n = 1.0/10.0
	#lambda_0 = lambda_n * n
	beta = 0.3
	delta = 0.01
	c = 4
	protocol = "PBFT"
	times = []

	for n in n_vals:
		lambda_0 = lambda_n * n
		e = Elastico(n, lambda_0, beta, delta, c, protocol)
		time = e.run_epochs(1)
		times.append(time)

	print(n_vals)
	print(times)

	# time1 = e.get_identities()
	# time2 = e.broadcast_committees()
	# time3 = e.intra_committee_consensus()
	# time4 = e.final_consensus()
	# time5 = e.generate_epoch_rand()
	# print(time1)
	# print(time2)
	# print(time3)
	# print(time4)
	# print(time5)



if __name__ == '__main__':
	main()