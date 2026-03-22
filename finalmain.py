from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

#  DATA

courses = [
    {"id": 1, "title": "Python Basics", "instructor": "John", "category": "Web Dev", "level": "Beginner", "price": 0, "seats_left": 10},
    {"id": 2, "title": "React JS", "instructor": "Alice", "category": "Web Dev", "level": "Intermediate", "price": 2000, "seats_left": 5},
    {"id": 3, "title": "Data Science", "instructor": "Bob", "category": "Data Science", "level": "Advanced", "price": 5000, "seats_left": 3},
    {"id": 4, "title": "Design Basics", "instructor": "Emma", "category": "Design", "level": "Beginner", "price": 1500, "seats_left": 8},
    {"id": 5, "title": "Docker", "instructor": "Chris", "category": "DevOps", "level": "Intermediate", "price": 2500, "seats_left": 6},
    {"id": 6, "title": "Machine Learning", "instructor": "David", "category": "Data Science", "level": "Advanced", "price": 6000, "seats_left": 2}
]

enrollments = []
wishlist = []
enrollment_counter = 1

#  MODELS

class EnrollRequest(BaseModel):
    student_name: str = Field(..., min_length=2)
    course_id: int = Field(..., gt=0)
    email: str = Field(..., min_length=5)
    payment_method: str = "card"
    coupon_code: str = ""
    gift_enrollment: bool = False
    recipient_name: str = ""

class NewCourse(BaseModel):
    title: str = Field(..., min_length=2)
    instructor: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    level: str = Field(..., min_length=2)
    price: int = Field(..., ge=0)
    seats_left: int = Field(..., gt=0)

#  HELPERS

def find_course(course_id):
    return next((c for c in courses if c["id"] == course_id), None)

def calculate_fee(price, seats_left, coupon):
    final = price
    discount = 0

    if seats_left > 5:
        d = 0.1 * price
        final -= d
        discount += d

    if coupon == "STUDENT20":
        d = 0.2 * final
        final -= d
        discount += d
    elif coupon == "FLAT500":
        final -= 500
        discount += 500

    return max(final, 0), discount


@app.get("/")
def home():
    return {"message": "Welcome to LearnHub Online Courses"}

@app.get("/courses")
def get_courses():
    return {
        "courses": courses,
        "total": len(courses),
        "total_seats_available": sum(c["seats_left"] for c in courses)
    }

@app.get("/courses/summary")
def summary():
    return {
        "total_courses": len(courses),
        "free_courses": len([c for c in courses if c["price"] == 0]),
        "most_expensive": max(courses, key=lambda x: x["price"]),
        "total_seats": sum(c["seats_left"] for c in courses),
        "category_count": {c["category"]: len([x for x in courses if x["category"] == c["category"]]) for c in courses}
    }

@app.get("/courses/{course_id}")
def get_course(course_id: int):
    course = find_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    return course

@app.get("/enrollments")
def get_enrollments():
    return {"data": enrollments, "total": len(enrollments)}



@app.post("/enrollments")
def enroll(req: EnrollRequest):
    global enrollment_counter

    course = find_course(req.course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    if course["seats_left"] <= 0:
        raise HTTPException(400, "No seats available")

    if req.gift_enrollment and not req.recipient_name:
        raise HTTPException(400, "Recipient required")

    fee, discount = calculate_fee(course["price"], course["seats_left"], req.coupon_code)

    course["seats_left"] -= 1

    record = {
        "id": enrollment_counter,
        "student": req.student_name,
        "course": course["title"],
        "final_fee": fee,
        "discount": discount,
        "recipient": req.recipient_name if req.gift_enrollment else None
    }

    enrollments.append(record)
    enrollment_counter += 1

    return record

@app.get("/courses/filter")
def filter_courses(category: Optional[str] = None, level: Optional[str] = None,
                   max_price: Optional[int] = None, has_seats: Optional[bool] = None):

    data = courses

    if category:
        data = [c for c in data if c["category"] == category]
    if level:
        data = [c for c in data if c["level"] == level]
    if max_price is not None:
        data = [c for c in data if c["price"] <= max_price]
    if has_seats is True:
        data = [c for c in data if c["seats_left"] > 0]

    return data

@app.post("/courses", status_code=201)
def create_course(course: NewCourse):
    if any(c["title"] == course.title for c in courses):
        raise HTTPException(400, "Duplicate course")
    new = course.dict()
    new["id"] = len(courses) + 1
    courses.append(new)
    return new

@app.put("/courses/{course_id}")
def update_course(course_id: int, price: Optional[int] = None, seats_left: Optional[int] = None):
    course = find_course(course_id)
    if not course:
        raise HTTPException(404, "Not found")
    if price is not None:
        course["price"] = price
    if seats_left is not None:
        course["seats_left"] = seats_left
    return course

@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    course = find_course(course_id)
    if not course:
        raise HTTPException(404, "Not found")
    if any(e["course"] == course["title"] for e in enrollments):
        raise HTTPException(400, "Cannot delete enrolled course")
    courses.remove(course)
    return {"message": "Deleted"}

@app.post("/wishlist/add")
def add_wishlist(student_name: str, course_id: int):
    if not find_course(course_id):
        raise HTTPException(404, "Course not found")
    if any(w["student"] == student_name and w["course_id"] == course_id for w in wishlist):
        raise HTTPException(400, "Already added")
    wishlist.append({"student": student_name, "course_id": course_id})
    return {"message": "Added"}

@app.get("/wishlist")
def get_wishlist():
    total = sum(find_course(w["course_id"])["price"] for w in wishlist)
    return {"wishlist": wishlist, "total_value": total}

@app.delete("/wishlist/remove/{course_id}")
def remove_wishlist(course_id: int, student_name: str):
    for w in wishlist:
        if w["course_id"] == course_id and w["student"] == student_name:
            wishlist.remove(w)
            return {"message": "Removed"}
    raise HTTPException(404, "Not found")

@app.post("/wishlist/enroll-all")
def enroll_all(student_name: str):
    total_fee = 0
    enrolled = []

    for w in wishlist[:]:
        if w["student"] == student_name:
            course = find_course(w["course_id"])
            if course and course["seats_left"] > 0:
                fee, _ = calculate_fee(course["price"], course["seats_left"], "")
                course["seats_left"] -= 1
                total_fee += fee
                enrolled.append(course["title"])
                wishlist.remove(w)

    return {"enrolled_courses": enrolled, "total_fee": total_fee}


@app.get("/courses/search")
def search_courses(keyword: str):
    data = [c for c in courses if keyword.lower() in c["title"].lower()
            or keyword.lower() in c["category"].lower()
            or keyword.lower() in c["instructor"].lower()]
    return {"results": data, "total": len(data)}

@app.get("/courses/sort")
def sort_courses(sort_by: str = "price"):
    if sort_by not in ["price", "title", "seats_left"]:
        raise HTTPException(400, "Invalid field")
    return sorted(courses, key=lambda x: x[sort_by])

@app.get("/courses/page")
def page_courses(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    return courses[start:start + limit]

@app.get("/enrollments/search")
def search_enroll(student_name: str):
    return [e for e in enrollments if student_name.lower() in e["student"].lower()]

@app.get("/enrollments/sort")
def sort_enroll():
    return sorted(enrollments, key=lambda x: x["final_fee"])

@app.get("/enrollments/page")
def page_enroll(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    return enrollments[start:start + limit]

@app.get("/courses/browse")
def browse(keyword: Optional[str] = None, category: Optional[str] = None,
           level: Optional[str] = None, max_price: Optional[int] = None,
           sort_by: str = "price", page: int = 1, limit: int = 3):

    data = courses

    if keyword:
        data = [c for c in data if keyword.lower() in c["title"].lower()]
    if category:
        data = [c for c in data if c["category"] == category]
    if level:
        data = [c for c in data if c["level"] == level]
    if max_price:
        data = [c for c in data if c["price"] <= max_price]

    data = sorted(data, key=lambda x: x[sort_by])

    start = (page - 1) * limit
    return data[start:start + limit]