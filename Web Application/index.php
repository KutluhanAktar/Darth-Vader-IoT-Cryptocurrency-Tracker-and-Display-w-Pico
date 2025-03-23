<?php

#Define the cryptocurrency_tracker class and its functions.
class cryptocurrency_tracker{
	
	private $currencies = [];
	
	# Get information as to the requested cryptocurrency - Bitcoin, Ethereum, etc.
	private function display_currency($cryptocurrency){
		# Make an HTTP Get request to the CoinGecko API V3 to collate data on the requested coin.
		$data = json_decode(file_get_contents("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=".$cryptocurrency, TRUE));
        # Create the query array with the requested data:
		$query = array(
			"name" => $data[0]->name,
			"price" => $data[0]->current_price,
			"total_volume" => $data[0]->total_volume,
			"price_change_24h" => $data[0]->price_change_24h,
			"percent_change_usd_24" => $data[0]->price_change_percentage_24h		
		);
		// Assign objects for each given coin:
		$this->currencies[$cryptocurrency] = $query;
	}
	
	# Print all requested cryptocurrencies.
	public function print_cryptocurrencies($cryptocurrencies){
		foreach($cryptocurrencies as $coin){
			$this->display_currency($coin);
		}
		echo(json_encode($this->currencies));
	}
}

# Define the new 'coin' class object.
$coin = new cryptocurrency_tracker();
# Get data on this list of cryptocurrencies: Bitcoin, Ethereum, Binance Coin, XRP, Tether
$coin->print_cryptocurrencies(array("bitcoin", "ethereum", "binancecoin", "ripple", "tether"));

?>