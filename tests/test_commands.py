"""
Unit tests for commands module
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from commands.local_handlers import (
    TimeHandler, DateHandler, MathHandler, ConversionHandler
)
from commands.router import CommandRouter


class TestTimeHandler:
    """Test time command handler"""
    
    def test_can_handle_time_queries(self):
        """Test time query recognition"""
        handler = TimeHandler()
        
        assert handler.can_handle("what time is it") is True
        assert handler.can_handle("What's the time?") is True
        assert handler.can_handle("tell me the clock") is True
        assert handler.can_handle("hello world") is False
    
    @patch('commands.local_handlers.datetime')
    def test_handle_time_query(self, mock_datetime):
        """Test time query handling"""
        # Mock the current time
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2:30 PM"
        mock_datetime.now.return_value = mock_now
        
        handler = TimeHandler()
        result = handler.handle("what time is it")
        
        assert result.response == "The time is 2:30 PM"
        assert result.command_type == "time"
        assert result.success is True
        assert "timestamp" in result.metadata


class TestDateHandler:
    """Test date command handler"""
    
    def test_can_handle_date_queries(self):
        """Test date query recognition"""
        handler = DateHandler()
        
        assert handler.can_handle("what date is it") is True
        assert handler.can_handle("what day is today") is True
        assert handler.can_handle("tell me today's date") is True
        assert handler.can_handle("what time is it") is False
    
    @patch('commands.local_handlers.datetime')
    def test_handle_date_query(self, mock_datetime):
        """Test date query handling"""
        # Mock the current date
        mock_now = MagicMock()
        mock_now.strftime.return_value = "Monday, January 15, 2024"
        mock_now.date.return_value.isoformat.return_value = "2024-01-15"
        mock_datetime.now.return_value = mock_now
        
        handler = DateHandler()
        result = handler.handle("what date is it")
        
        assert result.response == "Today is Monday, January 15, 2024"
        assert result.command_type == "date"
        assert result.success is True
        assert result.metadata["date"] == "2024-01-15"


class TestMathHandler:
    """Test math command handler"""
    
    def test_can_handle_math_queries(self):
        """Test math query recognition"""
        handler = MathHandler()
        
        assert handler.can_handle("what is 2 plus 3") is True
        assert handler.can_handle("calculate 10 times 5") is True
        assert handler.can_handle("5 + 7") is True
        assert handler.can_handle("hello world") is False
        assert handler.can_handle("what time is it") is False
    
    def test_handle_addition(self):
        """Test addition calculation"""
        handler = MathHandler()
        result = handler.handle("what is 2 plus 3")
        
        assert "2.0 plus 3.0 equals 5" in result.response
        assert result.command_type == "math"
        assert result.success is True
    
    def test_handle_subtraction(self):
        """Test subtraction calculation"""
        handler = MathHandler()
        result = handler.handle("what is 10 minus 4")
        
        assert "10.0 minus 4.0 equals 6" in result.response
        assert result.command_type == "math"
        assert result.success is True
    
    def test_handle_multiplication(self):
        """Test multiplication calculation"""
        handler = MathHandler()
        result = handler.handle("what is 6 times 7")
        
        assert "6.0 times 7.0 equals 42" in result.response
        assert result.command_type == "math"
        assert result.success is True
    
    def test_handle_division(self):
        """Test division calculation"""
        handler = MathHandler()
        result = handler.handle("what is 15 divided by 3")
        
        assert "15.0 divided by 3.0 equals 5" in result.response
        assert result.command_type == "math"
        assert result.success is True
    
    def test_handle_division_by_zero(self):
        """Test division by zero error"""
        handler = MathHandler()
        result = handler.handle("what is 5 divided by 0")
        
        assert result.success is False
        assert "couldn't understand" in result.response.lower()
    
    def test_handle_invalid_math(self):
        """Test invalid math expression"""
        handler = MathHandler()
        result = handler.handle("what is hello plus world")
        
        assert result.success is False
        assert "couldn't understand" in result.response.lower()


class TestConversionHandler:
    """Test conversion command handler"""
    
    def test_can_handle_conversion_queries(self):
        """Test conversion query recognition"""
        handler = ConversionHandler()
        
        assert handler.can_handle("convert 32 fahrenheit to celsius") is True
        assert handler.can_handle("how many feet in 5 meters") is True
        assert handler.can_handle("100 pounds to kilograms") is True
        assert handler.can_handle("what time is it") is False
    
    def test_handle_temperature_conversion_f_to_c(self):
        """Test Fahrenheit to Celsius conversion"""
        handler = ConversionHandler()
        result = handler.handle("convert 32 fahrenheit to celsius")
        
        assert "32.0 degrees Fahrenheit is 0.0 degrees Celsius" in result.response
        assert result.command_type == "conversion"
        assert result.success is True
    
    def test_handle_temperature_conversion_c_to_f(self):
        """Test Celsius to Fahrenheit conversion"""
        handler = ConversionHandler()
        result = handler.handle("convert 0 celsius to fahrenheit")
        
        assert "0.0 degrees Celsius is 32.0 degrees Fahrenheit" in result.response
        assert result.command_type == "conversion"
        assert result.success is True
    
    def test_handle_length_conversion_feet_to_meters(self):
        """Test feet to meters conversion"""
        handler = ConversionHandler()
        result = handler.handle("convert 3 feet to meters")
        
        assert "3.0 feet is" in result.response
        assert "meters" in result.response
        assert result.command_type == "conversion"
        assert result.success is True
    
    def test_handle_invalid_conversion(self):
        """Test invalid conversion"""
        handler = ConversionHandler()
        result = handler.handle("convert hello to world")
        
        assert result.success is False
        assert "couldn't understand" in result.response.lower()


class TestCommandRouter:
    """Test command router"""
    
    def test_register_and_route_handler(self):
        """Test registering handlers and routing commands"""
        router = CommandRouter()
        time_handler = TimeHandler()
        
        router.register_handler(time_handler)
        
        route_type, result = router.route_command("what time is it")
        
        assert route_type == "local"
        assert result.command_type == "time"
        assert "time is" in result.response.lower()
    
    def test_route_to_ai_when_no_handler(self):
        """Test routing to AI when no local handler matches"""
        router = CommandRouter()
        
        route_type, result = router.route_command("tell me a joke")
        
        assert route_type == "ai"
        assert result.command_type == "ai_query"
    
    def test_contains_question_with_question_mark(self):
        """Test question detection with question mark"""
        router = CommandRouter()
        
        assert router.contains_question("What is your name?") is True
        assert router.contains_question("This is a statement.") is False
    
    def test_contains_question_with_question_words(self):
        """Test question detection with question words"""
        router = CommandRouter()
        
        assert router.contains_question("What time is it") is True
        assert router.contains_question("How are you") is True
        assert router.contains_question("Can you help me") is True
        assert router.contains_question("Tell me about yourself") is False
    
    def test_multiple_handlers(self):
        """Test multiple handlers registration and routing"""
        router = CommandRouter()
        
        # Register multiple handlers
        router.register_handler(TimeHandler())
        router.register_handler(DateHandler())
        router.register_handler(MathHandler())
        
        # Test time query
        route_type, result = router.route_command("what time is it")
        assert route_type == "local"
        assert result.command_type == "time"
        
        # Test date query
        route_type, result = router.route_command("what date is it")
        assert route_type == "local"
        assert result.command_type == "date"
        
        # Test math query
        route_type, result = router.route_command("what is 5 plus 5")
        assert route_type == "local"
        assert result.command_type == "math"
        
        # Test AI fallback
        route_type, result = router.route_command("tell me about the weather")
        assert route_type == "ai"
        assert result.command_type == "ai_query"