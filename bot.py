#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, Optional, Any, Union
import sys
import os
import time
import requests
from datetime import datetime
import anthropic
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from utils.logger import logger
from utils.browser import browser
from config import config

class ETHBTCCorrelationBot:
    def __init__(self) -> None:
        self.browser = browser
        self.config = config
        self.session = requests.Session()
        self.claude_client = anthropic.Client(api_key=self.config.CLAUDE_API_KEY)
        self.session.timeout = (30, 90)  # (connect, read) timeouts
        logger.log_startup()

    def start(self) -> None:
        """Main bot execution loop"""
        try:
            retry_count = 0
            max_setup_retries = 3
            
            while retry_count < max_setup_retries:
                if not self.browser.initialize_driver():
                    retry_count += 1
                    logger.logger.warning(f"Browser initialization attempt {retry_count} failed, retrying...")
                    time.sleep(10)
                    continue
                    
                if not self._login_to_twitter():
                    retry_count += 1
                    logger.logger.warning(f"Twitter login attempt {retry_count} failed, retrying...")
                    time.sleep(15)
                    continue
                    
                break
            
            if retry_count >= max_setup_retries:
                raise Exception("Failed to initialize bot after maximum retries")

            logger.logger.info("Bot initialized successfully")

            while True:
                try:
                    self._run_correlation_cycle()
                    time.sleep(self.config.CORRELATION_INTERVAL * 60)
                except Exception as e:
                    logger.log_error("Correlation Cycle", str(e), exc_info=True)
                    time.sleep(5 * 60)
                    continue

        except KeyboardInterrupt:
            logger.logger.info("Bot stopped by user")
        except Exception as e:
            logger.log_error("Bot Execution", str(e), exc_info=True)
        finally:
            self._cleanup()

    def _get_crypto_data(self) -> Optional[Dict[str, Any]]:
        """Fetch BTC and ETH data from CoinGecko with retries"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = self.session.get(
                    self.config.get_coingecko_markets_url(),
                    params=self.config.get_coingecko_params(),
                    timeout=(30, 90)
                )
                response.raise_for_status()
                logger.log_coingecko_request("/markets", success=True)
                
                data = {coin['symbol'].upper(): coin for coin in response.json()}
                
                if 'BTC' not in data or 'ETH' not in data:
                    logger.log_error("Crypto Data", "Missing BTC or ETH data")
                    return None
                
                return data
                
            except requests.exceptions.Timeout:
                retry_count += 1
                wait_time = retry_count * 10
                logger.logger.warning(f"CoinGecko timeout, attempt {retry_count}, waiting {wait_time}s...")
                time.sleep(wait_time)
                
            except Exception as e:
                logger.log_coingecko_request("/markets", success=False)
                logger.log_error("CoinGecko API", str(e))
                return None
        
        logger.log_error("CoinGecko API", "Maximum retries reached")
        return None
    def _login_to_twitter(self) -> bool:
        """Log into Twitter using environment credentials with enhanced verification"""
        try:
            logger.logger.info("Starting Twitter login sequence")
            self.browser.driver.set_page_load_timeout(45)
            self.browser.driver.get('https://twitter.com/login')
            logger.logger.info("Navigated to Twitter login page")
            time.sleep(5)  # Wait for initial page load

            # Enhanced username entry with WebDriverWait
            logger.logger.info("Attempting to enter username...")
            try:
                username_field = WebDriverWait(self.browser.driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[autocomplete='username']"))
                )
                username_field.click()
                time.sleep(1)
                username_field.send_keys(self.config.TWITTER_USERNAME)
                logger.logger.info("Username entered successfully")
            except Exception as e:
                logger.log_error("Twitter Login", f"Failed to enter username: {str(e)}")
                return False

            time.sleep(2)

            # Click next button using explicit wait
            logger.logger.info("Attempting to click next button...")
            try:
                next_button = WebDriverWait(self.browser.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
                )
                next_button.click()
                logger.logger.info("Next button clicked successfully")
            except Exception as e:
                logger.log_error("Twitter Login", f"Failed to click next: {str(e)}")
                return False

            time.sleep(3)

            # Enhanced password entry with WebDriverWait
            logger.logger.info("Attempting to enter password...")
            try:
                password_field = WebDriverWait(self.browser.driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']"))
                )
                password_field.click()
                time.sleep(1)
                password_field.send_keys(self.config.TWITTER_PASSWORD)
                logger.logger.info("Password entered successfully")
            except Exception as e:
                logger.log_error("Twitter Login", f"Failed to enter password: {str(e)}")
                return False

            time.sleep(2)

            # Take debug screenshot before login attempt
            self.browser.driver.save_screenshot("login_page_debug.png")
            logger.logger.info("Saved debug screenshot before login attempt")

            # Enhanced login button click using explicit XPath
            logger.logger.info("Attempting to click login button...")
            try:
                login_button = WebDriverWait(self.browser.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']"))
                )
                login_button.click()
                logger.logger.info("Login button clicked successfully")
            except Exception as e:
                logger.log_error("Twitter Login", f"Failed to click login: {str(e)}")
                return False

            # Wait 10 seconds for 2FA input
            logger.logger.info("Waiting 10 seconds for 2FA/Authy code input...")
            time.sleep(10)

            # Verify successful login
            return self._verify_login()

        except Exception as e:
            logger.log_error("Twitter Login", f"Login failed: {str(e)}", exc_info=True)
            return False

    def _verify_login(self) -> bool:
        """Verify successful Twitter login with enhanced verification"""
        try:
            logger.logger.info("Starting login verification")
            max_retries = self.config.MAX_RETRIES
            retry_count = 0
            
            while retry_count < max_retries:
                logger.logger.info(f"Verification attempt {retry_count + 2}/{max_retries}")
                
                verification_methods = [
                    lambda: WebDriverWait(self.browser.driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="SideNav_NewTweet_Button"]'))
                    ),
                    lambda: WebDriverWait(self.browser.driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="AppTabBar_Profile_Link"]'))
                    ),
                    lambda: WebDriverWait(self.browser.driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="primaryColumn"]'))
                    ),
                    lambda: any(path in self.browser.driver.current_url 
                              for path in ['home', 'twitter.com/home'])
                ]
                
                for i, method in enumerate(verification_methods, 1):
                    try:
                        if method():
                            logger.logger.info(f"Login verified successfully using method {i}")
                            return True
                    except Exception as e:
                        logger.logger.debug(f"Error in verification method {i}: {str(e)}")
                
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 8 * retry_count
                    logger.logger.info(f"Verification attempt failed, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    self.browser.wait_and_refresh(timeout=10)
            
            logger.log_error("Login Verification", f"Failed to verify login after {max_retries} attempts")
            return False
            
        except Exception as e:
            logger.log_error("Login Verification", f"Verification failed: {str(e)}")
            return False

    def _analyze_market_sentiment(self, crypto_data: Dict[str, Any]) -> Optional[str]:
        """Use Claude to analyze market sentiment and correlation with retries"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                btc = crypto_data['BTC']
                eth = crypto_data['ETH']
                
                prompt = self.config.CLAUDE_ANALYSIS_PROMPT.format(
                    btc_price=btc['current_price'],
                    btc_change=btc['price_change_percentage_24h'],
                    btc_volume=btc['total_volume'],
                    eth_price=eth['current_price'],
                    eth_change=eth['price_change_percentage_24h'],
                    eth_volume=eth['total_volume']
                )
                
                response = self.claude_client.messages.create(
                    model=self.config.CLAUDE_MODEL,
                    max_tokens=250,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                analysis = response.content[0].text
                return self._format_tweet_analysis(analysis, btc, eth)
                
            except Exception as e:
                retry_count += 1
                wait_time = retry_count * 10
                logger.logger.warning(f"Claude API error, attempt {retry_count}, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
        
        logger.log_error("Market Sentiment Analysis", "Maximum retries reached")
        return None

    def _format_tweet_analysis(self, analysis: str, btc: Dict[str, Any], eth: Dict[str, Any]) -> str:
        """Format Claude's analysis for Twitter, respecting length constraints"""
        base_tweet = (
            f"ETH/BTC Market Pulse - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"BTC: ${btc['current_price']:,.2f} ({btc['price_change_percentage_24h']:.2f}%)\n"
            f"ETH: ${eth['current_price']:,.2f} ({eth['price_change_percentage_24h']:.2f}%)\n\n"
        )
        
        full_tweet = base_tweet + analysis
        
        constraints = self.config.TWEET_CONSTRAINTS
        if len(full_tweet) > constraints['HARD_STOP_LENGTH']:
            full_tweet = full_tweet[:constraints['HARD_STOP_LENGTH'] - 3] + "..."
        
        if len(full_tweet) < constraints['MIN_LENGTH']:
            full_tweet += " #Crypto #ETH #BTC"
        
        return full_tweet

    def _post_analysis(self, tweet_text: str) -> bool:
        """Post correlation analysis to Twitter with retry mechanism"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Navigate to compose tweet page
                self.browser.driver.get('https://twitter.com/compose/tweet')
                time.sleep(3)
                
                # Use WebDriverWait for tweet text area
                text_area = WebDriverWait(self.browser.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
                )
                text_area.click()
                time.sleep(1)
                text_area.send_keys(tweet_text)
                time.sleep(2)

                # Enhanced post button detection and clicking
                post_button_locators = [
                    (By.CSS_SELECTOR, '[data-testid="tweetButton"]'),
                    (By.XPATH, "//div[@role='button'][contains(., 'Post')]"),
                    (By.XPATH, "//span[text()='Post']")
                ]

                post_button = None
                for locator in post_button_locators:
                    try:
                        post_button = WebDriverWait(self.browser.driver, 5).until(
                            EC.element_to_be_clickable(locator)
                        )
                        if post_button:
                            break
                    except:
                        continue

                if post_button:
                    # Scroll to button and click
                    self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", post_button)
                    time.sleep(1)
                    post_button.click()
                    time.sleep(5)
                    logger.logger.info("Tweet posted successfully")
                    return True
                else:
                    raise Exception("Could not find post button")
                
            except Exception as e:
                retry_count += 1
                wait_time = retry_count * 10
                logger.logger.warning(f"Tweet posting error, attempt {retry_count}, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
        
        logger.log_error("Tweet Creation", "Maximum retries reached")
        return False

    def _run_correlation_cycle(self) -> None:
        """Run correlation analysis and posting cycle"""
        try:
            crypto_data = self._get_crypto_data()
            if not crypto_data:
                return
            
            tweet_text = self._analyze_market_sentiment(crypto_data)
            if not tweet_text:
                return
            
            self._post_analysis(tweet_text)
        
        except Exception as e:
            logger.log_error("Correlation Cycle", str(e))

    def _cleanup(self) -> None:
        """Cleanup resources"""
        try:
            if self.browser:
                logger.logger.info("Closing browser...")
                try:
                    self.browser.close_browser()
                    time.sleep(1)
                except Exception as e:
                    logger.logger.warning(f"Error during browser close: {str(e)}")
            logger.log_shutdown()
        except Exception as e:
            logger.log_error("Cleanup", str(e))

if __name__ == "__main__":
    bot = ETHBTCCorrelationBot()
    bot.start()    
