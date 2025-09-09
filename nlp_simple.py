class SimpleNLPClassifier:
	"""
	Lightweight, dependency-free classifier providing scores for candidate labels.
	It uses keyword heuristics and simple token statistics to approximate relevance.
	Compatible with Python 3.13.3.
	"""

	def __init__(self):
		self.label_keywords = {
			"drug sale": [
				"sell", "sale", "price", "rate", "discount", "delivery", "stock", "supply",
				"available", "in stock", "dm", "whatsapp", "bulk", "wholesale", "cash on delivery",
				"stealth", "doorstep", "express", "guarantee", "list", "order"
			],
			"normal": [
				"hello", "hi", "thanks", "information", "news", "update", "discussion", "general",
				"chat", "topic", "share", "link"
			],
			"spam": [
				"free", "click", "subscribe", "follow", "promo", "offer", "win", "limited",
				"contest", "bonus", "referral", "ad", "advertisement"
			],
			"other": []
		}

		# Common drug-related terms to boost "drug sale"
		self.drug_terms = [
			"mdma", "lsd", "mephedrone", "cocaine", "heroin", "cannabis", "marijuana",
			"ganja", "charas", "hash", "hashish", "weed", "pot", "ecstasy", "molly",
			"meth", "crystal meth", "acid", "brown sugar", "white powder", "maal"
		]

	def __call__(self, text, candidate_labels):
		"""
		Mimic transformers pipeline interface:
		return {"labels": [best_label,...], "scores": [best_score,...]}
		We compute a per-label score in [0,1] using keyword hits and density.
		"""
		text_lower = (text or "").lower()

		# Token count for normalization; avoid division by zero
		num_chars = max(1, len(text_lower))

		label_to_score = {}

		for label in candidate_labels:
			keywords = self.label_keywords.get(label, [])
			base_score = 0.0

			# Keyword matches
			for kw in keywords:
				if kw and kw in text_lower:
					# Weight by keyword length for specificity
					base_score += min(0.05 + (len(kw) / 200.0), 0.15)

			# Additional boost for drug terms when evaluating "drug sale"
			if label == "drug sale":
				for drug_kw in self.drug_terms:
					if drug_kw in text_lower:
						base_score += 0.12
				# Heuristic for presence of currency/price pattern
				if any(sym in text_lower for sym in ["$", "₹", "rs ", "price", "rate", "k "]):
					base_score += 0.12
				# Contact/transaction signals
				if any(sig in text_lower for sig in ["dm", "whatsapp", "telegram", "contact", "deal", "order"]):
					base_score += 0.08

			# Normalize into [0, 1]
			label_to_score[label] = max(0.0, min(1.0, base_score))

		# Soft fallback: if all zero, mark as normal with small confidence
		if all(score == 0.0 for score in label_to_score.values()):
			label_to_score = {label: (0.2 if label == "normal" else 0.0) for label in candidate_labels}

		# Sort labels by score descending
		sorted_labels = sorted(candidate_labels, key=lambda l: label_to_score.get(l, 0.0), reverse=True)
		sorted_scores = [label_to_score.get(l, 0.0) for l in sorted_labels]

		return {
			"labels": sorted_labels,
			"scores": sorted_scores
		}


