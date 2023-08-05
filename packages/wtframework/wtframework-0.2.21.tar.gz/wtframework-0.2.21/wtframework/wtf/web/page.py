##########################################################################
#This file is part of WTFramework. 
#
#    WTFramework is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    WTFramework is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with WTFramework.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################


from datetime import datetime, timedelta
from wtframework.wtf.config import WTF_CONFIG_READER, WTF_TIMEOUT_MANAGER
from wtframework.wtf.utils import wait_utils
from wtframework.wtf.utils.debug_utils import print_debug
from wtframework.wtf.utils.wait_utils import do_until
from wtframework.wtf.web.capture import WebScreenShotUtil
from wtframework.wtf.web.webdriver import WTF_WEBDRIVER_MANAGER
import abc
import time


class PageObject(object):
    '''
    Baseclass for PageObjects.
    
    Basic Usage:
    1) define '_validate_page' method.  This method will check to make sure 
       we are on the correct page.
    2) define '__cmp__' method to allow page ranking when there are multiple matches 
       to the same page to disambiguate which page should take precedence.
    '''
    __metaclass__ = abc.ABCMeta #needed to make this an abstract class in Python 2.7

    # Webdriver associated with this instance of the PageObject

    __names_of_classes_we_already_took_screen_caps_of__ = {}


    def __init__(self, webdriver, *args, **kwargs):
        '''
        Constructor
        @param webdriver: Instance of Selenium WebDriver
        @type webdriver: WebDriver
        '''
        try:
            config_reader=kwargs['config_reader']
        except KeyError:
            config_reader=WTF_CONFIG_READER

        
        self._validate_page(webdriver)
        
        # Assign webdriver to PageObject. 
        # Each page object has an instance of "webdriver" referencing the webdriver 
        # driving this page.
        self.webdriver = webdriver

        # Take reference screenshots if this option is enabled.
        if config_reader.get("selenium.take_reference_screenshot", False) == True:
            class_name = type(self).__name__
            if class_name in PageObject.__names_of_classes_we_already_took_screen_caps_of__:
                pass
            else:
                try:
                    WebScreenShotUtil.take_reference_screenshot(webdriver, class_name)
                    PageObject.__names_of_classes_we_already_took_screen_caps_of__[class_name] = True
                except Exception as e:
                    print e # Some WebDrivers such as head-less drivers does not take screenshots.
        else:
            pass


    @abc.abstractmethod
    def _validate_page(self, webdriver):
        """
        Perform checks to validate this page is the correct target page.
        
        All pages must implement this method.
        
        @raise InvalidPageError: Raised when we try to assign the wrong page 
        to this page object.  This exception should be raised when a page match 
        fails.  Any other exception type would be consider a code failure.
        """
        return


    @classmethod
    def create_page(cls, webdriver=None, **kwargs):
        """
        Class method short cut to call PageFactory on itself.
        @param webdriver: WebDriver to associate with this page.
        @type webdriver: WebDriver
        """
        if not webdriver:
            webdriver = WTF_WEBDRIVER_MANAGER.get_driver()
        return PageFactory.create_page(cls, webdriver=webdriver, **kwargs)


    #Magic methods for enabling comparisons.
    def __cmp__(self, other):
        """
        Override this to implement PageObject ranking.  This is used by PageObjectFactory
        when it finds multiple pages that qualify to map to the current page.  The 
        PageObjectFactory will check which page object is preferable.
        """
        if not isinstance(other, PageObject):
            # By default page object will rank itself over non page objects.
            return 1;
        else:
            return 0


class InvalidPageError(Exception):
    '''Thrown when we have tried to instantiate the incorrect page to a PageObject.'''
    pass



class PageFactory():
    "Page Factory class for constructing PageObjects."

    @staticmethod
    def create_page(page_object_class_or_interface, \
                    webdriver=None, **kwargs):
        """
        Instantiate a page object from a given Interface or Abstract class.
        
        Instantiating a Page from PageObject from class usage:
            my_page_instance = PageFactory.create_page(MyPageClass)
        
        Instantiating a Page from an Interface or base class
            import pages.mysite.* 
            my_page_instance = PageFactory.create_page(MyPageInterfaceClass)
        
        Instantiating a Page from a list of classes.
            my_page_instance = PageFactory.create_page([PossiblePage1, PossiblePage2])
        
        Note: It'll only be able to detect pages that are imported.  To it's best to 
        do an import of all pages implementing a base class or the interface inside the 
        __init__.py of the package directory.  
        
        @param  page_object_class_or_interface: Class, AbstractBaseClass, or Interface to attempt to consturct.
        @param webdriver: Selenium Webdriver to use to instantiate the page.
        @type webdriver: WebDriver
        """
        
        if not webdriver:
            webdriver = WTF_WEBDRIVER_MANAGER.get_driver()
        
        # will be used later when tracking best matched page.
        current_matched_page = None
        
        
        # Walk through all classes of this sub class 
        if type(page_object_class_or_interface) == list:
            subclasses = []
            for page_class in page_object_class_or_interface:
                #attempt to instantiate class.
                page = PageFactory.__instantiate_page_object(page_class, \
                                                             webdriver, \
                                                             **kwargs)
                if isinstance(page, PageObject) and (current_matched_page == None or page > current_matched_page):
                    current_matched_page = page
                
                #check for subclasses
                subclasses += PageFactory.__itersubclasses(page_class)
        else:
            # Try the original class
            page_class = page_object_class_or_interface
            page = PageFactory.__instantiate_page_object(page_class, \
                                                         webdriver, \
                                                         **kwargs)
            if isinstance(page, PageObject):
                current_matched_page = page

            #check for subclasses
            subclasses = PageFactory.__itersubclasses(page_object_class_or_interface)

        # Iterate over subclasses of the passed in classes to see if we have a better match.
        for pageClass in subclasses :
            try:
                page = pageClass(webdriver, **kwargs)
                if current_matched_page == None or page > current_matched_page:
                    current_matched_page = page
            except InvalidPageError as e:
                print_debug("InvalidPageError", e)
                pass #This happens when the page fails check.
            except TypeError as e:
                print_debug("TypeError", e)
                pass #this happens when it tries to instantiate the original abstract class.
            except Exception as e:
                print_debug("Exception", e)
                #Unexpected exception.
                raise e

        # If no matching classes.
        if not isinstance(current_matched_page, PageObject):
            raise NoMatchingPageError("There's, no matching classes to this page. URL:%s" \
                                      % webdriver.current_url)
        else:
            return current_matched_page

    @staticmethod
    def __instantiate_page_object(page_obj_class, webdriver, **kwargs):
        try:
            page = page_obj_class(webdriver, **kwargs)
            return page
        except InvalidPageError:
            pass #This happens when the page fails check.
        except TypeError:
            pass #this happens when it tries to instantiate the original abstract class.
        except Exception as e:
            #Unexpected exception.
            raise e

    @staticmethod
    def __itersubclasses(cls, _seen=None):
        """
        Credit goes to: http://code.activestate.com/recipes/576949-find-all-subclasses-of-a-given-class/
        
        itersubclasses(cls)
    
        Generator over all subclasses of a given class, in depth first order.
    
        >>> list(itersubclasses(int)) == [bool]
        True
        >>> class A(object): pass
        >>> class B(A): pass
        >>> class C(A): pass
        >>> class D(B,C): pass
        >>> class E(D): pass
        >>> 
        >>> for cls in itersubclasses(A):
        ...     print(cls.__name__)
        B
        D
        E
        C
        >>> # get ALL (new-style) classes currently defined
        >>> [cls.__name__ for cls in itersubclasses(object)] #doctest: +ELLIPSIS
        ['type', ...'tuple', ...]
        """
        if not isinstance(cls, type):
            raise TypeError('Argument (%s) passed to PageFactory does not appear to be a valid Class.' % cls, \
                            "Check to make sure the first parameter is an PageObject class, interface, or mixin.")
        if _seen is None: _seen = set()
        try:
            subs = cls.__subclasses__()
        except TypeError: # fails only when cls is type
            subs = cls.__subclasses__(cls)
        for sub in subs:
            if sub not in _seen:
                _seen.add(sub)
                yield sub
                for sub in PageFactory.__itersubclasses(sub, _seen):
                    yield sub



class NoMatchingPageError(RuntimeError):
    "Raised when no matching page object is not found."
    pass


class PageObjectUtils():
    '''
    Offers utility methods that are useful for use within PageObjects..
    '''

    @staticmethod
    def check_css_selectors(webdriver, *selectors):
        """
        Returns true if all CSS selectors passed in is found.  This can be used 
        to quickly validate a page.
        
        Usage Example:
        if not PageObjectUtils.check_css_selectors("form#loginForm", "submit.login"):
            raise InvalidPageError("This is not the login page.")

        @param webdriver: WebDriver.
        @type webdriver: WebDriver 
        @param *selectors: CSS selector for element to look for.
        @type *selectors: str
        """
        for selector in selectors:
            try:
                webdriver.find_element_by_css_selector(selector)
            except:
                return False # A selector failed.

        return True # All selectors succeeded



class PageUtils():
    '''
    Offers utility methods that operate on a page level.
    '''
    
    @staticmethod
    def wait_until_page_loaded(page_obj_class, 
                               webdriver=None,
                               timeout=WTF_TIMEOUT_MANAGER.NORMAL, 
                               sleep=0.5, 
                               bad_page_classes=[], **kwargs):
        """
        Waits until the page is loaded.
        
        Usage Example: 
            webdriver.get("http://www.mysite.com/login")
            # Wait up to 60 seconds for the page to load.
            login_page = wait_until_page_loaded(LoginPage, timeout=60)
        
        @return: Returns PageObject of type passed in.
        @rtype: PageObject
        """
        if not webdriver:
            webdriver = WTF_WEBDRIVER_MANAGER.get_driver()
        
        #convert this param to list if not already.
        if type(bad_page_classes) != list:
            bad_page_classes = [bad_page_classes]
        
        end_time = datetime.now() + timedelta(seconds = timeout)
        last_exception = None
        while datetime.now() < end_time:
            # Check to see if we're at our target page.
            try:
                page = PageFactory.create_page(page_obj_class, webdriver=webdriver, **kwargs)
                PageUtils.wait_until_page_ready(page)
                return page
            except Exception as e:
                last_exception = e
                pass
            # Check to see if we're at one of those labled 'Bad' pages.
            for bad_page_class in bad_page_classes:
                try:
                    PageFactory.create_page(bad_page_class, webdriver=webdriver, **kwargs)
                    #if the if/else statement succeeds, than we have an error.
                    raise BadPageEncounteredError("Encountered a bad page. " + bad_page_class.__name__)
                except BadPageEncounteredError as e:
                    raise e
                except:
                    pass #We didn't hit a bad page class yet.
            #sleep till the next iteration.
            time.sleep(sleep)

        print "Unable to construct page, last exception", last_exception
        raise PageLoadTimeoutError("Timedout while waiting for {page} to load. Url:{url}".\
                              format(page=PageUtils.__get_name_for_class__(page_obj_class), 
                                     url=webdriver.current_url))


    @staticmethod
    def wait_until_page_ready(pageobject, timeout=WTF_TIMEOUT_MANAGER.NORMAL):
        "Waits until document.readyState == Complete"
        try:
            do_until(lambda: pageobject.webdriver.execute_script("return document.readyState").lower() \
                     =='complete', timeout)
        except wait_utils.OperationTimeoutError:
            raise PageUtilOperationTimeoutError("Timeout occurred while waiting for page to be ready.")
        


    @staticmethod
    def __get_name_for_class__(class_or_list):
        if type(class_or_list) == list:
            name = "["
            for item in class_or_list:
                name += PageUtils.__get_name_for_class__(item) + ","
            name += "]"
            return name
        else:
            try:
                return class_or_list.__name__
            except:
                return str(class_or_list)


class PageUtilOperationTimeoutError(Exception):
    "Timed out while waiting for a WebUtil action"
    pass


class BadPageEncounteredError(Exception):
    "Raised when a bad page is encountered."
    pass

class PageLoadTimeoutError(PageUtilOperationTimeoutError):
    "Timeout while waiting for page to load."
    pass