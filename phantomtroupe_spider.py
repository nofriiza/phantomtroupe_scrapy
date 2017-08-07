import scrapy


class MangakuSpider(scrapy.Spider):
	name = 'mangaku'

	start_urls = ['http://mangaku.web.id/daftar-komik-bahasa-indonesia/']
	def parse(self, response):
		manga_list = response.css("div.series_alpha")
		for x in manga_list:
			lists = x.css("ul.series_alpha li")
			for y in lists:
				link = y.css("a::attr(href)").extract_first()
				data = {
					"title" : y.css("a::text").extract_first(),
					"cover" : y.css("a::attr(rel)").extract_first(),
					"link_chapter" : link
				}
				if data['title']:
					if data['title'].strip() == "18+":
						continue
				else:
					data['title'] = y.css("a::attr(title)").extract_first()
				request = scrapy.Request(url=link,callback=self.parse_manga)
				request.meta['title'] = data['title'].strip()
				yield request
				# yield response.follow(link,self.parse_manga,meta={"data":data})

	def parse_manga(self,response):
		fbroot = response.css("div.entry div#fb-root").extract_first()
		if fbroot is not None:
			request = scrapy.Request(url=response.url,callback=self.parse_image)
			request.meta['chapter_name'] = response.css("h2.titles a::text").extract_first()
			request.meta['link_read'] = response.url
			request.meta['title'] = response.meta['title']
			# yield request
		else :
			potong = response.css("table td")
			chapter_list = potong.css("small a")
			if ".jpg" in chapter_list.extract_first() or not chapter_list:
				chapter_list = potong.css("div a")
			for x in chapter_list:
				chapter_name = x.css("a::text").extract_first()
				link = x.css("a::attr(href)").extract_first()
				if 'mangaku' in link or 'is.gd' in link:
					request = scrapy.Request(url=link,callback=self.parse_image)
					request.meta['chapter_name'] = chapter_name
					request.meta['link_read'] = link
					request.meta['title'] = response.meta['title']
					yield request
					# yield response.follow(link,self.parse_image,meta={"data":data})


	def parse_image(self,response):
		list_images = response.css("div#contentwrap")
		list_image = list_images.css("img")
		if not list_image:
			list_image2 = list_images.css("center")
			list_image = list_image2.css("div.separator a img")

		if not list_image:
			list_image2 = list_images.css("center")
			list_image = list_image2.css("center a div#manga img")

		if not list_image:
			list_image2 = list_images.css("center")
			list_image = list_image2.css("p img")
		halaman = 1
		for x in list_image:
			link_gambar = x.css("img::attr(src)").extract_first()
			if not link_gambar:
				link_gambar = x.css("img.picture::attr(src)").extract_first()
			yield {
				"manga_name" : response.meta['title'],
				"chapter_name" : response.meta['chapter_name'],
				"link_read" : response.meta['link_read'],
				"halaman" : halaman,
				"link_gambar" : link_gambar,
			}
			halaman += 1

class AnimeindonetSpider(scrapy.Spider):
	name = 'animeindonet'

	start_urls = ['http://animeindo.net/anime-list','http://animeindo.net/movie-list']

	def start_request(self):
		for x in self.start_urls:
			yield scrapy.Request(x,self.parse)

	def parse(self, response):
		char_list = response.css("div.list ul")
		for x in char_list:
			anime_list = x.css("a.series")
			for y in anime_list:
				link = y.css("a::attr(href)").extract_first()
				title = y.css("a::text").extract_first()
				if title.startswith('.') or title.startswith('“') or title.startswith('['):
					continue
				request = scrapy.Request(url=link,callback=self.parse_anime)
				request.meta['title'] = title.strip()
				yield request

	def parse_anime(self,response):
		eps_list = response.css("ul.eps_lst li")
		counter = 0
		for x in eps_list:
			if counter == 0:
				counter += 1
				continue
			episode_title = x.css("a.c4::attr(title)").extract_first()
			link = x.css("a.c4::attr(href)").extract_first()
			yield {
				"anime_title" : response.meta['title'],
				"episode_title" : episode_title,
				"episode" : counter,
				"link_watch" : link,
			}

class OploverzSpider(scrapy.Spider):
	name = 'oploverz'

	start_urls = ['http://www.oploverz.in/series/']
	download_delay = 2

	def parse(self, response):
		anime_list = response.css("div.movlist")
		for x in anime_list:
			first_char = x.css("span a::text").extract_first()
			lists = x.css("ul li")
			counter = 0
			for y in lists:
				link = y.css('a::attr(href)').extract_first()
				yield response.follow(link,self.parse_anime)

	def parse_anime(self,response):
		info = response.css("div.animeinfos")
		sinopsis = info.css("span.desc p::text").extract_first()
		table = info.css("div.episodelist ul li")
		counter = 0
		for x in table:
			episode = x.css("span.leftoff a::text").extract_first().strip()
			title = x.css("span.lefttitle a::text").extract_first().strip()
			tgl_posting = x.css("span.rightoff::text").extract_first().strip()
			link = x.css("span.watch a::attr(href)").extract_first().strip()
			yield response.follow(link,self.parse_download)


	def parse_download(self,response):
		infox = response.css("div.op-download")
		title = response.css("h1.title::text").extract_first()
		for info in infox:			
			list_nama_file = info.css("div.title-download::text").extract()
			list_a = info.css("div.list-download")
			for x in list_nama_file:
				for y in list_a:
					counter = 0
					nama_server = y.css("a")
					for z in nama_server:
						nama_server = z.css("a::text").extract_first() if z.css("a::text").extract_first() else z.css("a strong::text").extract_first()
						link_download = y.css("a::attr(href)").extract()[counter]
						counter = counter +1
						yield {
							"title" : title,
							"nama_file" : x,
							"link_download" : link_download,
							"server_download" : nama_server,
						}

class SamehadakuSpider(scrapy.Spider):
	name = 'samehadaku'

	start_urls = ['https://www.samehadaku.net/2014/08/anime-list-subtitle-indonesia.html']
	download_delay = 1

	def parse(self, response):
		anime_list = response.css("p")
		for x in anime_list:
			title = x.css("strong a::text").extract_first()
			url = x.css("strong a::attr(href)").extract_first()
			if title is None:
				title = x.css("a strong::text").extract_first()
				url = x.css("a::attr(href)").extract_first()
			if title is None:
				title = x.css("a span::text").extract_first()
				url = x.css("a::attr(href)").extract_first()
			if url and title and title != "Daftar Anime Subtitle Indonesia":
				yield response.follow(url,self.parse_anime)


	def parse_anime(self,response):
		title_anime = response.css("h1.page-title").extract_first()
		anime_list = response.css("article")
		for x in anime_list:
			title_episode = x.css("h3.entry-title a::text").extract_first().strip()
			link = x.css("h3.entry-title a::attr(href)").extract_first()
			yield response.follow(link,self.parse_download)
		next_link = response.css("a.next::attr(href)").extract_first()
		if next_link:
			yield response.follow(next_link,self.parse_anime)


	def parse_download(self,response):
		title_anime = response.css("h1 strong::text").extract_first()
		if not title_anime:
			title_anime = response.css("h1::text").extract_first()
		block_download = response.css("div.download-eps ul li")
		if block_download:
			for x in block_download:
				resolusi = x.css("strong::text").extract_first()
				list_server = x.css("a")
				for y in list_server:
					server_name = y.css("a::text").extract_first()
					if server_name is None:
						server_name = y.css("a span::text").extract_first()
					link_download = y.css("a::attr(href)").extract_first()
					yield {
						"nama_anime" : title_anime,
						"resolusi" : resolusi,
						"server_download" : server_name,
						"link_download" : link_download,
					}
		else :
			block_download = response.css("p span")
			if block_download:
				for x in block_download:
					resolusi = None
					list_server = x.css("a")
					for y in list_server:
						server_name = y.css("a span strong::text").extract_first()
						if server_name is None:
							server_name = y.css("a span::text").extract_first()
						if server_name is None:
							server_name = y.css("a span b::text").extract_first()
						link_download = y.css("a::attr(href)").extract_first()
						if server_name is not None and "[" in server_name and "LIKE" not in server_name:
							yield {
								"nama_anime" : title_anime,
								"resolusi" : resolusi,
								"server_download" : server_name.strip(),
								"link_download" : link_download
							}