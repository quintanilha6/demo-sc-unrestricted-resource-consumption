# Demonstration Project for Managing Unrestricted Resource Consumption

## Introduction
This repository focuses on addressing on demonstrating some risks associated with unrestricted resource consumption within a web-based address validation service. The topic was chosen as part of a voluntary initiative to deepen understanding of system vulnerabilities and to demonstrate practical defense mechanisms against potential exploitation. The project serves as a hands-on educational tool to explore various security features and optimizations that enhance application robustness and resilience.

Some of the stategies to protect against Unrestricted Resource Consumption are:

1. **Resource Quotas**
2. **Timeouts**
3. **Concurrency Limits**
4. **Input Validation**
5. **Efficiency Enhancements**

## Strategies Explained

### 1. Resource Quotas
- **Definition:** Limits the amount of resources a user or process can consume, such as API calls or data throughput.
- **Example:** API Call Limit: Implement a quota that restricts the number of address validation requests a user can make per minute to prevent system overload.
    ```python
    if not feature_flags.check_and_increment_quota():
        resp.media = {
            'status': 'error',
            'message': 'Quota exceeded. Please wait until your quota resets before retrying.'
        }
        resp.status = falcon.HTTP_429
    ```

### 2. Timeouts
- **Definition:** Timeouts specify a maximum time limit that a process or transaction can take. If the operation exceeds this limit, it is terminated to free up system resources.
- **Example:** External API Timeout: Implement a quota that restricts the number of address validation requests a user can make per minute to prevent system overload.
    ```python
    try:
        response = requests.post(url, json={'address': address}, timeout=3)  # 3 seconds timeout
            except requests.exceptions.Timeout:
        raise TimeoutException("The request to the external service timed out.")

    ```

### 3. Concurrency Limits
- **Definition:** Concurrency limits restrict the number of simultaneous operations that can occur. This helps in preventing system overload by too many concurrent processes.
- **Example:** Limit Simultaneous Requests: Use a semaphore or a similar mechanism to limit the number of concurrent address validations that can be processed. This prevents excessive load on the server or the external API.
    ```python
    from asyncio import Semaphore

    semaphore = Semaphore(10)  # Allows up to 10 concurrent requests

    async def validate_address(req, resp):
        async with semaphore:
            # Perform address validation
            pass
    ```

### 4. Input Validation
- **Definition:** Input validation ensures that the incoming data is correctly formatted, valid, and secure before processing. This reduces the risk of injection attacks and errors that can consume undue resources.
- **Example:** Validate Address Input: Before sending an address to an external API, validate its format and check for any malicious content to ensure it adheres to expected patterns.
    ```python
    def validate_address_input(self, address):
        pattern = re.compile(r'^[a-zA-Z0-9 ,.-]+$')
        return pattern.match(address) is not None
    ```

### 5. Efficiency Enhancements
- **Definition:**  Improvements in code and system architecture that allow processes to use fewer resources, thereby increasing throughput and reducing latency.
- **Example:** Caching Successful Validations: Implement caching to store the results of previously validated addresses. This reduces the need to perform redundant external API calls for addresses that have been validated before, saving time and resources.
    ```python
    cache = {}

    def get_validated_address(address):
        if address in cache:
            return cache[address]
        result = external_validate_address(address)
        cache[address] = result
        return result
    ```

## How to run the app?
- Run the 3 apps (internal api, external api and UI) with docker-compose `docker-compose up -d --build`
- Check the logs for each of the apis with `docker-compose logs -f external_api` and `docker-compose logs -f internal_api`